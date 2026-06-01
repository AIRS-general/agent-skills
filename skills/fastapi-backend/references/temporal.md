## Temporal

A stateful distributed state machine for long-running code.

Temporal’s Python SDK is async-first: connecting and making RPC calls to Temporal are implemented as async operations.

### Concepts

1. Workflow (the central concept)
A Workflow is your business logic written as code.

A workflow is a function that can run for minutes, hours, or days — and still *survive failures*.

Key property: **Durable execution** (it remembers state even if the server crashes)

2. Activity
An Activity is a single unit of real work.

Examples:
* call an API
* train a model
* read from database
* send email

3. Worker

A worker is the process that runs your code.
- executes the workflow
- executes activities
- polls Temporal server for tasks

You can scale workers horizontally.

4. Temporal server (control plane)

The Temporal server is the "brain" of the system.

It handles:
- workflow state storage
- scheduling
- retries
- timers
- execution history

5. Task Queue

A Task Queue routes work to workers.
- workflow and activities are assigned to queues.
- workers listen to queues.

6. **Workflow execution state**
Temporal tracks:
- every step executed
- inputs/outputs
- retries
- failures

You can restart a crashed workflow where it left off.

7. Determinism

Workflows must be deterministic. 

Meaning: same inputs -> same execution path

Temporal can replay workflows safely after failure.

8. Signals

Signals are external events sent into a running workflow.

Example:
- user approves request
- dataset upload completed
- human-in-the-loop response

9. Queries

Queries allow you to inspect workflow state without modifying it.

Example:
- what is training loss?
- what step is running?

10. Timers (durability feature)

Temporal supports:
- sleep for hours/days
- retry delays
- scheduled execution

Even if the server restarts: timer still fire correctly.

11. Retries (built-in reliability)

Temporal automatically handles:
- retires with backoff
- failure recovery
- timeout handling

You define policies like:
- max retries
- exponential backoff
- non-retryable errors

### Example: Temporal for ML pipeline

`ingestion → validation → training → evaluation`
* Workflow
* Activities
* Worker
* Client

1. Install
```bash
uv add install temporalio
```

Run temporal locally:
```bash
docker run --rm -it -p 7233:7233 temporalio/auto-setup
```

2. Activities (`activities.py`)
Activities contain the actual work.

```py
from temporalio import activity
import time
import random


@activity.defn
async def ingest_data(dataset_id: str) -> str:
    print(f"Ingesting dataset: {dataset_id}")
    time.sleep(2)

    return f"/data/{dataset_id}.csv"


@activity.defn
async def validate_data(path: str) -> bool:
    print(f"Validating: {path}")
    time.sleep(2)

    return True


@activity.defn
async def train_model(path: str) -> str:
    print(f"Training model using {path}")
    time.sleep(5)

    model_id = f"model-{random.randint(1000,9999)}"

    return model_id


@activity.defn
async def evaluate_model(model_id: str) -> float:
    print(f"Evaluating model: {model_id}")
    time.sleep(2)

    accuracy = round(random.uniform(0.8, 0.99), 4)

    return accuracy
```

3. Workflow (`workflows.py`)
Workflow orchestrates the activities.

```py
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import (
        ingest_data,
        validate_data,
        train_model,
        evaluate_model,
    )


@workflow.defn
class MLTrainingWorkflow:

    @workflow.run
    async def run(self, dataset_id: str) -> dict:

        # Step 1: Ingestion
        dataset_path = await workflow.execute_activity(
            ingest_data,
            dataset_id,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Step 2: Validation
        is_valid = await workflow.execute_activity(
            validate_data,
            dataset_path,
            start_to_close_timeout=timedelta(minutes=5),
        )

        if not is_valid:
            raise ValueError("Dataset validation failed")

        # Step 3: Training
        model_id = await workflow.execute_activity(
            train_model,
            dataset_path,
            start_to_close_timeout=timedelta(hours=1),
        )

        # Step 4: Evaluation
        accuracy = await workflow.execute_activity(
            evaluate_model,
            model_id,
            start_to_close_timeout=timedelta(minutes=10),
        )

        return {
            "model_id": model_id,
            "accuracy": accuracy,
        }
```

4. Worker (`worker.py`)
Worker executes workflows and activities.

```py
import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import MLTrainingWorkflow
from activities import (
    ingest_data,
    validate_data,
    train_model,
    evaluate_model,
)


async def main():

    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="ml-task-queue",
        workflows=[MLTrainingWorkflow],
        activities=[
            ingest_data,
            validate_data,
            train_model,
            evaluate_model,
        ],
    )

    print("Worker started...")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
```

5. Start workflow (`run_workflow.py`)

```py
import asyncio

from temporalio.client import Client

from workflows import MLTrainingWorkflow


async def main():

    client = await Client.connect("localhost:7233")

    result = await client.execute_workflow(
        MLTrainingWorkflow.run,
        "soil_dataset_001",
        id="ml-workflow-001",
        task_queue="ml-task-queue",
    )

    print("Workflow result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

6. Run everything
Terminal 1
Start temporal server:
```bash
docker run --rm -it -p 7233:7233 temporalio/auto-setup
```

Terminal 2
Start worker:
```bash
python worker.py
```

Terminal 3
Run workflow:
```bash
python run_workflow.py
```

7. What makes this powerful? 
if:
- worker crashes
- machine reboots
- network disconnects

Temporal:
- remembers workflow state
- retries activities 
- resumes execution automatically

8. Important design rules
Workflow code should contain:
- orchestration logic
- branching
- retries
- sequencing

Activity code should contain:
- API calls
- ML training
- DB access
- GPU computation
- Side effects

### With Ray
Temporal orchestrates.
Ray performs GPU training.

```py
@activity.defn
async def train_model(path: str):
  # submit Ray job here
```

### Backend - Temporal - Worker

In a typical Temporal architecture, the backend application, Temporal server, and workers communicate indirectly through the Temporal service.

```
┌─────────────┐
│   Backend   │
│ Starts WF   │
└──────┬──────┘
       │ Temporal SDK
       ▼
┌─────────────────┐
│ Temporal Server │
│ Task Queues     │
│ Workflow State  │
│ History         │
└──────┬──────────┘
       │ Poll
       ▼
┌─────────────┐
│   Worker    │
│ WF + Acts   │
└─────────────┘
```

1. Backend -> Temporal Server

Your backend (REST API, GraphQL, gRPC service, etc.) uses the Temporal SDK.

```py
handle = await client.start_workflow(
    TrainingWorkflow.run,
    training_config,
    id=f"training-{job_id}",
    task_queue="training-queue",
)
```
The backend does not talk directly to workers.
Instead it tells Temporal: `Start workflow X on queue Y.`
Temporal stores this request in its database.

2. Worker -> Temporal Server
Workers continuously poll Temporal:

The workers run in a independent process.

```py
worker = Worker(
    client,
    task_queue="training-queue",
    workflows=[TrainingWorkflow],
    activities=[train_model],
)

await worker.run()
```
Conceptually:
```
Worker:
    "Any work on training-queue?"
Temporal:
    "Yes, run workflow 123."
```
Workers pull work from Temporal.
Temporal never pushes work directly.
