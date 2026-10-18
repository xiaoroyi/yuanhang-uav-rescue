import copy
import time

from fastapi.testclient import TestClient
import pytest

from backend.app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "runtime")) as c:
        yield c


def mission(client, template="compact", key="create-one"):
    response=client.post("/api/v1/missions",json={"name":"V2 isolated mission","template":template,"idempotency_key":key})
    assert response.status_code==201,response.text
    return response.json()


def test_mission_draft_publish_and_conflict(client):
    m=mission(client,"blank")
    assert m["current_scenario_id"] is None and m["draft"]["base"] is None
    draft=copy.deepcopy(m["draft"])
    saved=client.put(f"/api/v1/missions/{m['mission_id']}/draft",json={"expected_revision":1,"draft":draft})
    assert saved.status_code==200
    assert client.put(f"/api/v1/missions/{m['mission_id']}/draft",json={"expected_revision":1,"draft":draft}).status_code==409
    assert client.put(f"/api/v1/missions/{m['mission_id']}/draft",json={"expected_revision":2,"draft":draft,"publish":True}).status_code==422
    report=client.post(f"/api/v1/missions/{m['mission_id']}/preflight",json={"expected_revision":2}).json()
    assert report["blocking_count"]>0
    assert any(c["code"]=="WEATHER_NOT_CONFIGURED" and c["status"]=="unknown" for c in report["checks"])


def test_mission_idempotence_legacy_link_and_archive(client):
    m=mission(client)
    assert mission(client)==m
    assert client.post("/api/v1/missions",json={"name":"different","template":"compact","idempotency_key":"create-one"}).status_code==409
    original=client.get("/api/v1/scenarios/"+m["current_scenario_id"]).json()
    report=client.post(f"/api/v1/missions/{m['mission_id']}/preflight",json={"expected_revision":1}).json()
    assert report["blocking_count"]==0,report
    assert client.get("/api/v1/preflight-reports/"+report["report_id"]).json()==report
    archived=client.patch(f"/api/v1/missions/{m['mission_id']}",json={"expected_revision":1,"archived":True})
    assert archived.status_code==200 and archived.json()["lifecycle"]=="archived"
    assert client.get("/api/v1/scenarios/"+m["current_scenario_id"]).json()==original


def test_stage_totals_match_real_solver(client):
    m=mission(client)
    s=client.get("/api/v1/scenarios/"+m["current_scenario_id"]).json()
    snap=client.post(f"/api/v1/scenarios/{s['scenario_id']}/snapshots",json={"expected_state_version":1}).json()
    response=client.post("/api/v1/solve-jobs",json={"snapshot_id":snap["snapshot_id"],"time_limit_s":2})
    assert response.status_code==202,response.text
    job=response.json()
    for _ in range(240):
        job=client.get("/api/v1/solve-jobs/"+job["job_id"]).json()
        if job["job_state"] not in ("queued","running"):break
        time.sleep(.05)
    assert job["has_validated_plan"],job
    p=client.get("/api/v1/plans/"+job["plan_id"]).json()
    a=client.get(f"/api/v1/plans/{p['plan_id']}/stages")
    assert a.status_code==200,a.text
    for r in p["sorties"]:
        rows=[x for x in a.json()["trajectory_segments"] if x["sortie_id"]==r["sortie_id"]]
        assert sum(x["energy_kwh"] for x in rows)==pytest.approx(r["energy_kwh"])
        assert rows[-1]["soc_end"]==pytest.approx(r["return_soc"])
        assert rows[0]["start_s"]==r["prepare_start_s"]
        assert rows[-1]["end_s"]==pytest.approx(r["drone_released_s"],abs=1e-6)
        assert set(x["phase"] for x in rows)>={"prepare","cruise","handover"}
