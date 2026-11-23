from datetime import date,datetime
import gzip,hashlib,json,zipfile
import pandas as pd
import pytest
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.database.base import Base
from app.database.models import AnalysisRun,EodIngestionBatch,Nifty50EodBar,NiftyOptionEodBar
from app.database.session import get_db
from app.main import app
from app.modules.data_processing.normalization import normalize_index,normalize_options,ProcessingValidationError

@pytest.fixture()
def fixture_client(tmp_path,monkeypatch):
    root=tmp_path;raw=root/"artifacts/raw/nse";(root/"artifacts/manifests").mkdir(parents=True)
    for folder in ("fo_bhavcopy","mii_contracts","nifty50_ohlc"):(raw/folder).mkdir(parents=True)
    day=date(2026,11,19); dmy=day.strftime("%d%m%Y"); ymd=day.strftime("%Y%m%d")
    bhpath=raw/"fo_bhavcopy"/f"BhavCopy_NSE_FO_0_0_0_{ymd}_F_0000.csv.zip"
    bh=pd.DataFrame([
    {"TradDt":day.isoformat(),"FinInstrmId":1001,"TckrSymb":"NIFTY","OptnTp":"CE","XpryDt":"2026-11-26","StrkPric":26000,"OpnPric":90,"HghPric":110,"LwPric":80,"ClsPric":100,"TtlTradgVol":10,"OpnIntrst":200,"UndrlygPric":26000},
    {"TradDt":day.isoformat(),"FinInstrmId":1002,"TckrSymb":"NIFTY","OptnTp":"PE","XpryDt":"2026-11-26","StrkPric":26000,"OpnPric":0,"HghPric":0,"LwPric":0,"ClsPric":0,"TtlTradgVol":0,"OpnIntrst":300,"UndrlygPric":26000}])
    tmp=root/"bh.csv";bh.to_csv(tmp,index=False)
    with zipfile.ZipFile(bhpath,"w",zipfile.ZIP_DEFLATED) as z:z.write(tmp,"bh.csv")
    exp=int((datetime(2026,11,26)-datetime(1980,1,1)).total_seconds())
    mii=pd.DataFrame([{"FinInstrmId":1001,"TckrSymb":"NIFTY","OptnTp":"CE","XpryDt":exp,"StrkPric":2600000},{"FinInstrmId":1002,"TckrSymb":"NIFTY","OptnTp":"PE","XpryDt":exp,"StrkPric":2600000}])
    mipath=raw/"mii_contracts"/f"NSE_FO_contract_{dmy}.csv.gz";mii.to_csv(mipath,index=False,compression="gzip")
    ixpath=raw/"nifty50_ohlc"/f"ind_close_all_{dmy}.csv"
    pd.DataFrame([{"Index Name":"NIFTY 50","Index Date":day.strftime("%d-%m-%Y"),"Open Index Value":25900,"High Index Value":26100,"Low Index Value":25800,"Closing Index Value":26000}]).to_csv(ixpath,index=False)
    def ent(path):
        data=path.read_bytes();return {"status":"DOWNLOADED","path":str(path.relative_to(root)),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"url":"https://archives.nseindia.com/reports"}
    (root/"artifacts/manifests/fo-download-manifest.json").write_text(json.dumps({"results":[{"date":day.isoformat(),"bhavcopy":ent(bhpath),"mii_contract":ent(mipath)}]}))
    (root/"artifacts/manifests/nifty50-download-manifest.json").write_text(json.dumps({"results":[{"date":day.isoformat(),**ent(ixpath)}]}))
    monkeypatch.setenv("DATA_STORAGE_PATH",str(root))
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
    def override():
        db=factory()
        try:yield db
        finally:db.close()
    app.dependency_overrides[get_db]=override
    client=TestClient(app)
    request={"analysis_date":day.isoformat(),"idempotency_key":"phase3-processing-test-001"}
    created=client.post("/api/v1/analysis-runs",json=request);assert created.status_code==201,created.text
    yield client,day,created.json(),factory,bhpath,[bhpath,mipath,ixpath]
    client.close();app.dependency_overrides.clear();engine.dispose()

def test_normalization_retains_zero_volume_rows_and_contract_types():
    day=date(2026,11,19);expiry=date(2026,11,26);exp=int((datetime(2026,11,26)-datetime(1980,1,1)).total_seconds())
    bh=pd.DataFrame([{"TradDt":day.isoformat(),"FinInstrmId":7,"TckrSymb":"NIFTY","OptnTp":"PE","XpryDt":expiry.isoformat(),"StrkPric":26000,"OpnPric":0,"HghPric":0,"LwPric":0,"ClsPric":0,"TtlTradgVol":0,"OpnIntrst":3,"UndrlygPric":26000}])
    mii=pd.DataFrame([{"FinInstrmId":7,"TckrSymb":"NIFTY","OptnTp":"PE","XpryDt":exp,"StrkPric":2600000}])
    result=normalize_options(bh,mii,None,day,expiry,26000)
    assert len(result)==1 and result[0]["volume"]==0 and result[0]["option_type"]=="PE"

def test_corrupt_or_mismatched_contract_is_rejected():
    day=date(2026,11,19);expiry=date(2026,11,26);exp=int((datetime(2026,11,26)-datetime(1980,1,1)).total_seconds())
    bh=pd.DataFrame([{"TradDt":day.isoformat(),"FinInstrmId":7,"TckrSymb":"NIFTY","OptnTp":"CE","XpryDt":expiry.isoformat(),"StrkPric":26000,"OpnPric":10,"HghPric":12,"LwPric":9,"ClsPric":11,"TtlTradgVol":1,"OpnIntrst":3,"UndrlygPric":26000}])
    mii=pd.DataFrame([{"FinInstrmId":7,"TckrSymb":"NIFTY","OptnTp":"CE","XpryDt":exp,"StrkPric":2600100}])
    with pytest.raises(ProcessingValidationError,match="metadata mismatch"):normalize_options(bh,mii,None,day,expiry,26000)

def test_process_endpoint_persists_idempotently_and_exposes_read_model(fixture_client):
    client,day,run,factory,_,_=fixture_client;url=f"/api/v1/analysis-runs/{run['id']}/process"
    first=client.post(url);assert first.status_code==200,first.text;assert first.json()["status"]=="COMPLETED"
    second=client.post(url);assert second.status_code==200 and second.json()["id"]==first.json()["id"]
    status=client.get(f"/api/v1/analysis-runs/{run['id']}/processing");assert status.status_code==200
    processed=client.get(f"/api/v1/analysis-runs/{run['id']}/processed-data");assert processed.status_code==200
    assert len(processed.json()["option_rows"])==2
    assert processed.json()["validation"]["zero_volume_rows"]==1
    db=factory()
    try:
        assert db.scalar(select(AnalysisRun).where(AnalysisRun.id==run["id"])).status=="PROCESSED"
        assert len(list(db.scalars(select(NiftyOptionEodBar))))==2
        assert len(list(db.scalars(select(Nifty50EodBar))))==1
    finally:db.close()

def test_source_file_bytes_remain_unchanged_on_success(fixture_client):
    client,_,run,_,_,sources=fixture_client;before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in sources]
    assert client.post(f"/api/v1/analysis-runs/{run['id']}/process").status_code==200
    after=[hashlib.sha256(p.read_bytes()).hexdigest() for p in sources]
    assert before==after
