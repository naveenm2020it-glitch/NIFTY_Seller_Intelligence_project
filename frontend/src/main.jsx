import React,{useEffect,useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import {getAnalysisDates,resolveConfiguration,startAnalysis} from "./services/api";
import "./style.css";
function App(){
 const [dates,setDates]=useState([]),[analysisDate,setAnalysisDate]=useState(""),[expiry,setExpiry]=useState("");
 const [preview,setPreview]=useState(null),[loadingDates,setLoadingDates]=useState(true),[loadingPreview,setLoadingPreview]=useState(false);
 const [starting,setStarting]=useState(false),[run,setRun]=useState(null),[error,setError]=useState("");
 useEffect(()=>{getAnalysisDates().then(v=>{setDates(v);if(v.length)setAnalysisDate(v[v.length-1]);}).catch(e=>setError(e.message)).finally(()=>setLoadingDates(false));},[]);
 useEffect(()=>{if(!analysisDate){setPreview(null);setExpiry("");return undefined;}let cancelled=false;setLoadingPreview(true);setError("");setRun(null);
  resolveConfiguration(analysisDate,expiry||undefined).then(v=>{if(cancelled)return;setPreview(v);if(!expiry||!v.available_expiries.includes(expiry))setExpiry(v.selected_expiry);})
   .catch(e=>{if(!cancelled){setPreview(null);setError(e.message);}}).finally(()=>{if(!cancelled)setLoadingPreview(false);});
  return()=>{cancelled=true;};
 },[analysisDate,expiry]);
 const canStart=useMemo(()=>Boolean(preview&&!loadingPreview&&!starting),[preview,loadingPreview,starting]);
 async function handleStart(){if(!preview||starting)return;setStarting(true);setError("");setRun(null);
  try{setRun(await startAnalysis({analysis_date:analysisDate,expiry:expiry||null,idempotency_key:crypto.randomUUID()}));}
  catch(e){setError(e.message);}finally{setStarting(false);}}
 return <main className="page">
  <header className="topbar"><div className="brand-mark">NS</div><div><p className="eyebrow">Historical EOD workspace</p><h1>NIFTY Seller Intelligence</h1></div><span className="phase-tag">Phase 2 · Configuration</span></header>
  <section className="intro"><p className="eyebrow">Analysis setup</p><h2>Choose a session. Review the expiry. Start only when ready.</h2><p>Historical NIFTY options data is checked against the preserved Phase 1 archive. Selecting a date or expiry only previews the configuration; it does not start a run.</p></section>
  <section className="panel"><div className="section-heading"><div><p className="eyebrow">01 / Configuration</p><h3>Analysis inputs</h3></div><span className="read-only">EOD only</span></div>
   {loadingDates?<p className="muted">Loading audited sessions…</p>:<div className="field-grid">
    <label className="field"><span>Analysis date</span><select value={analysisDate} onChange={e=>{setAnalysisDate(e.target.value);setExpiry("");}} disabled={!dates.length}>{dates.map(d=><option key={d} value={d}>{new Date(d+"T00:00:00").toLocaleDateString("en-IN",{day:"2-digit",month:"short",year:"numeric"})}</option>)}</select><small>Only sessions with all three audited source files are listed.</small></label>
    <label className="field"><span>Expiry</span><select value={expiry} onChange={e=>setExpiry(e.target.value)} disabled={!preview||loadingPreview}>{preview?.available_expiries.map(d=><option key={d} value={d}>{new Date(d+"T00:00:00").toLocaleDateString("en-IN",{day:"2-digit",month:"short",year:"numeric"})}</option>)}</select><small>Nearest available expiry is automatic; another listed expiry can be selected.</small></label>
   </div>}
   {loadingPreview&&<p className="muted">Checking manifests, file integrity and available expiries…</p>}
   {preview&&!loadingPreview&&<div className="review"><div><span className="review-label">Resolved expiry</span><strong>{preview.selected_expiry}</strong></div><span className={preview.expiry_selection_mode==="AUTO"?"mode auto":"mode"}>{preview.expiry_selection_mode==="AUTO"?"Automatic":"Manual selection"}</span>{preview.automatic_fallback&&<p className="notice">{preview.fallback_reason}</p>}</div>}
   <div className="actions"><button onClick={handleStart} disabled={!canStart}>{starting?"Validating…":"Start Analysis"}</button><span className="muted">Changing inputs does not retrieve data or start analysis.</span></div>
  </section>
  {error&&<div className="error" role="alert"><strong>Unable to continue</strong><span>{error}</span></div>}
  {run&&<section className="panel result"><div className="section-heading"><div><p className="eyebrow">02 / Run record</p><h3>Inputs validated</h3></div><span className="run-status">{run.status.replaceAll("_"," ")}</span></div>
   <dl className="run-grid"><div><dt>Run ID</dt><dd>{run.id}</dd></div><div><dt>Analysis date</dt><dd>{run.analysis_date}</dd></div><div><dt>Selected expiry</dt><dd>{run.selected_expiry} · {run.expiry_selection_mode}</dd></div></dl>
   <p className="muted">Phase 2 validates and hands off the source set. Analytical processing has not run.</p><ol className="stages">{run.stage_results.map(s=><li key={s.stage}><span>{s.stage.replaceAll("_"," ")}</span><b>{s.status}</b></li>)}</ol>
  </section>}
  <footer><span>Phase 2 scope · Configuration & orchestration</span><span>No live data · No trading execution</span></footer>
 </main>;
}
createRoot(document.getElementById("root")).render(<React.StrictMode><App/></React.StrictMode>);
