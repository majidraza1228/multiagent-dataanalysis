---
name: mlflow-tracking
description: MLflow experiment tracking, model registry, and run comparison snippets
---

```python
# setup experiment + run context
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("cifar10-classifier")

with mlflow.start_run(run_name="cnn-v1") as run:
    # log params
    mlflow.log_params({"lr": 1e-3, "batch_size": 128, "epochs": 50, "optimizer": "adam"})

    # log metrics (call inside training loop)
    mlflow.log_metric("val_accuracy", 0.874, step=10)
    mlflow.log_metric("train_loss", 0.312, step=10)

    # log artifact
    mlflow.log_artifact("checkpoints/model.pt", artifact_path="model")

    print("Run ID:", run.info.run_id)
```

```python
# register model to registry
import mlflow.pytorch
import torch

model = torch.load("checkpoints/model.pt", map_location="cpu")
with mlflow.start_run():
    mlflow.pytorch.log_model(
        model,
        artifact_path="model",
        registered_model_name="cifar10-cnn",
    )

# tag version
client = mlflow.tracking.MlflowClient()
client.set_registered_model_tag("cifar10-cnn", "stage", "production")
client.set_model_version_tag("cifar10-cnn", "1", "validated", "true")
```

```python
# load model from registry
import mlflow.pytorch

model = mlflow.pytorch.load_model("models:/cifar10-cnn/Production")
model.eval()
```

```python
# compare_runs.py — fetch all runs, sort by val_accuracy, print table
import mlflow
from tabulate import tabulate

mlflow.set_tracking_uri("http://localhost:5000")
client = mlflow.tracking.MlflowClient()

experiment = client.get_experiment_by_name("cifar10-classifier")
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.val_accuracy DESC"],
)

rows = [
    [r.info.run_id[:8], r.data.params.get("lr"), r.data.params.get("epochs"),
     round(r.data.metrics.get("val_accuracy", 0), 4)]
    for r in runs
]
print(tabulate(rows, headers=["run_id", "lr", "epochs", "val_accuracy"], tablefmt="grid"))
```

```bash
# start mlflow server
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```
