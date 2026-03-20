import mlflow
from tabulate import tabulate

mlflow.set_tracking_uri("http://localhost:5000")
client = mlflow.tracking.MlflowClient()

experiment = client.get_experiment_by_name("excel-sheet-analysis")
if experiment is None:
    print("No experiment named 'excel-sheet-analysis' found. Run training first.")
else:
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.overall_quality DESC"],
    )
    rows = [
        [run.info.run_id[:8], run.info.run_name, round(run.data.metrics.get("overall_quality", 0), 4)]
        for run in runs
    ]
    print(tabulate(rows, headers=["run_id", "name", "overall_quality"], tablefmt="grid"))
