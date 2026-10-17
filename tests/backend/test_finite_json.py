import json

from fastapi.testclient import TestClient

from backend.app.main import create_app
from solver.adapters.contest import compact_scenario


def test_nonfinite_model_parameters_are_structured_422_not_saved_or_server_error(
    tmp_path,
):
    with TestClient(create_app(tmp_path / "runtime")) as client:
        scene = compact_scenario()
        for value in [float("nan"), float("inf"), float("-inf")]:
            scene["drone_types"][0]["energy_model"]["parameters"][
                "empty_range_m"
            ] = value
            response = client.post(
                "/api/v1/scenarios/import",
                content=json.dumps(scene),
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code == 422, response.text
            assert "non-finite" in response.json()["error"]["message"]
        assert client.get("/api/v1/scenarios").json() == []
