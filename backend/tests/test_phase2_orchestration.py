import gzip, hashlib, json, zipfile
from datetime import date, datetime
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.base import Base
from app.database.session import get_db
from app.main import app

@pytest.fixture()
def client(tmp_path, monkeypatch):
    root=tmp_path; raw=root/"artifacts/raw/nse"; (root/"artifacts/manifests").mkdir(parents=True)
    for folder in ("fo_bhavcopy","mii_contracts","nifty50_ohlc"): (raw/folder).mkdir(parents=True)
    day=date(2026,11,19); ymd=day.strftime("%Y%m%d"); dmy=day.strftime("%d%m%Y")
    bhpath=raw/"fo_bhavcopy"/f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"
    bh=pd.DataFrame([
      {"TradDt":day.isoformat(),"FinInstrmId":1001,"TckrSymb":"NIFTY","OptnTp":"CE","XpryDt":"2026-11-26","StrkPric":26000,"ClsPric":100,"TtlTradgVol":10,"OpnIntrst":20,"UndrlygPric":26000},
      {"TradDt":day.isoformat(),"FinInstrmId":1002,"TckrSymb":"NIFTY","OptnTp":"PE","XpryDt":"2026-12-03","StrkPric":2600000,"ClsPric":110,"TtlTradgVol":12,"OpnIntrst":30,"UndrlygPric":26000}])
    temp=root/"bh.csv"; bh.to_csv(temp,index=False)
    with zipfile.ZipFile(bhpath,"w",zipfile.ZIP_DEFLATED) as z:z.write(temp,"bh.csv")
    mipath=raw/"mii_contracts"/f"NSE_FO_contract_{dmy}.csv.gz"
    mii=pd.DataFrame([
      {"FinInstrmId":1001,"TckrSymb":"NIFTY","OptnTp":"CE","XpryDt":int((datetime(2026,11,26)-datetime(1980,1,1)).total_seconds()),"StrkPric":2600000},
      {"FinInstrmId":1002,"TckrSymb":"NIFTY","OptnTp":"PE","XpryDt":int((datetime(2026,12,3)-datetime(1980,1,1)).total_seconds()),"StrkPric":2600000}])
    mii.to_csv(mipath,index=False,compression="gzip")
    ixpath=raw/"nifty50_ohlc"/f"ind_close_all_{dmy}.csv"
    pd.DataFrame([{"Index Name":"NIFTY 50","Index Date":day.strftime("%d-%m-%Y"),"Open Index Value":25900,"High Index Value":26100,"Low Index Value":25800,"Closing Index Value":26000}]).to_csv(ixpath,index=False)
    def ent(path,url):
      data=path.read_bytes();return {"status":"DOWNLOADED","path":str(path.relative_to(root)),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"url":url}
    (root/"artifacts/manifests/fo-download-manifest.json").write_text(json.dumps({"results":[{"date":day.isoformat(),"bhavcopy":ent(bhpath,"https://archives.nseindia.com/bhavcopy"),"mii_contract":ent(mipath,"https://archives.nseindia.com/mii")}] }))
    (root/"artifacts/manifests/nifty50-download-manifest.json").write_text(json.dumps({"results":[{"date":day.isoformat(),**ent(ixpath,"https://archives.nseindia.com/index")}] }))
    monkeypatch.setenv("DATA_STORAGE_PATH",str(root))
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
    def override():
      db=factory()
      try:yield db
      finally:db.close()
    app.dependency_overrides[get_db]=override
    with TestClient(app) as c:yield c,day,bhpath
    app.dependency_overrides.clear();engine.dispose()

def test_preview_selects_nearest_expiry_and_does_not_create_run(client):
    c,day,_=client;r=c.get("/api/v1/configuration/resolve",params={"analysis_date":day.isoformat()})
    assert r.status_code==200 and r.json()["selected_expiry"]=="2026-11-26"
    assert r.json()["expiry_selection_mode"]=="AUTO"
    assert c.get("/api/v1/analysis-runs/not-created").status_code==404

def test_manual_expiry_override(client):
    c,day,_=client;r=c.get("/api/v1/configuration/resolve",params={"analysis_date":day.isoformat(),"expiry":"2026-12-03"})
    assert r.status_code==200 and r.json()["expiry_selection_mode"]=="MANUAL"

def test_start_persists_run_and_provenance(client):
    c,day,_=client;r=c.post("/api/v1/analysis-runs",json={"analysis_date":day.isoformat(),"idempotency_key":"phase2-test-key-001"})
    assert r.status_code==201;data=r.json()
    assert data["status"]=="READY_FOR_PROCESSING" and data["selected_expiry"]=="2026-11-26"
    assert data["source_provenance"]["content_checks"]["nifty_option_rows"]==2
    assert data["stage_results"][-1]["details"]["analytics_executed"] is False

def test_retry_is_idempotent_and_payload_conflict_rejected(client):
    c,day,_=client;p={"analysis_date":day.isoformat(),"idempotency_key":"phase2-test-key-002"}
    a=c.post("/api/v1/analysis-runs",json=p);b=c.post("/api/v1/analysis-runs",json=p)
    assert a.json()["id"]==b.json()["id"]
    assert c.post("/api/v1/analysis-runs",json={**p,"expiry":"2026-12-03"}).status_code==409

def test_corrupt_source_fails_safely(client):
    c,day,bhpath=client;bhpath.write_bytes(b"corrupt")
    r=c.post("/api/v1/analysis-runs",json={"analysis_date":day.isoformat(),"idempotency_key":"phase2-test-key-003"})
    assert r.status_code==422 and "SHA-256 mismatch" in r.json()["detail"]["message"]

def test_non_session_without_archive_data_is_rejected(client):
    c,_,_=client;r=c.get("/api/v1/configuration/resolve",params={"analysis_date":"2026-11-20"})
    assert r.status_code==422

def test_missing_archive_is_actionable(client,monkeypatch,tmp_path):
    c,_,_=client;monkeypatch.setenv("DATA_STORAGE_PATH",str(tmp_path/"empty"))
    r=c.get("/api/v1/configuration/analysis-dates")
    assert r.status_code==503 and "DATA_STORAGE_PATH" in r.json()["detail"]
