const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {...options, headers: {"Content-Type":"application/json",...(options.headers||{})}});
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) { const detail=payload.detail; throw new Error(typeof detail==="string"?detail:detail?.message||"Request failed."); }
  return payload;
}
export const getAnalysisDates=()=>request("/api/v1/configuration/analysis-dates");
export const resolveConfiguration=(day,expiry)=>{const p=new URLSearchParams({analysis_date:day});if(expiry)p.set("expiry",expiry);return request(`/api/v1/configuration/resolve?${p.toString()}`);};
export const startAnalysis=(payload)=>request("/api/v1/analysis-runs",{method:"POST",headers:{"Idempotency-Key":payload.idempotency_key},body:JSON.stringify(payload)});
