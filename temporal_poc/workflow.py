"""Temporal POC: orchestrate a UAT run as a durable workflow
(health check -> smoke tests -> regression -> AI analysis -> Jira report),
with automatic retries per step.

Run a local Temporal server first:  temporal server start-dev
Then:  python -m temporal_poc.workflow
"""

import asyncio
import subprocess
import sys
from datetime import timedelta

import requests
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

TASK_QUEUE = "uat-automation"


@activity.defn
async def check_env(base_url: str) -> str:
    requests.get(f"{base_url}/health", timeout=10).raise_for_status()
    return "healthy"


@activity.defn
async def run_pytest(marker: str) -> int:
    return subprocess.call([sys.executable, "-m", "pytest", "-m", marker, "-q"])


@activity.defn
async def post_process() -> str:
    subprocess.call([sys.executable, "-m", "ai_analysis.analyze_failures"])
    subprocess.call([sys.executable, "-m", "integrations.jira.jira_reporter"])
    return "reported"


@workflow.defn
class UatRunWorkflow:
    @workflow.run
    async def run(self, base_url: str) -> dict:
        opts = {"start_to_close_timeout": timedelta(minutes=30), "retry_policy": RetryPolicy(maximum_attempts=3)}
        await workflow.execute_activity(check_env, base_url, **opts)
        smoke = await workflow.execute_activity(run_pytest, "smoke", **opts)
        regression = -1
        if smoke == 0:
            regression = await workflow.execute_activity(run_pytest, "regression", **opts)
        await workflow.execute_activity(post_process, **opts)
        return {"smoke_exit": smoke, "regression_exit": regression}


async def main():
    client = await Client.connect("localhost:7233")
    async with Worker(
        client, task_queue=TASK_QUEUE, workflows=[UatRunWorkflow], activities=[check_env, run_pytest, post_process]
    ):
        result = await client.execute_workflow(
            UatRunWorkflow.run, "http://127.0.0.1:8000", id="uat-run-demo", task_queue=TASK_QUEUE
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
