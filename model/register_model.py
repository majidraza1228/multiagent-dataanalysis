import os
from pathlib import Path

import mlflow

PROFILE_PATH = Path("checkpoints/model.pt")
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def main():
    if not PROFILE_PATH.exists():
        raise FileNotFoundError("checkpoints/model.pt not found. Run `python model/train.py` first.")

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("excel-sheet-analysis")

    with mlflow.start_run(run_name="register-profile-artifact") as run:
        mlflow.log_artifact(str(PROFILE_PATH), artifact_path="model")
        print(f"Registered workbook profile artifact in run {run.info.run_id}")


if __name__ == "__main__":
    main()
