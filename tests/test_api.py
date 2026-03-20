import io

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def make_csv_bytes() -> bytes:
    return b"date,revenue,region\n2024-01-01,1200,EMEA\n2024-01-02,1400,NA\n"


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "model_version" in body
    assert "uptime" in body


def test_analyze_wrong_file_type():
    response = client.post(
        "/api/analyze",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "File must be" in response.json()["detail"]


def test_analyze_csv_returns_summary():
    response = client.post(
        "/api/analyze",
        files={"file": ("sales.csv", make_csv_bytes(), "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["workbook_name"] == "sales.csv"
    assert body["sheet_count"] == 1
    assert body["summary"]["total_rows"] == 2
    assert body["dataset_type"] in {"financial", "operations", "general_tabular"}
    assert len(body["sheet_summaries"]) == 1
