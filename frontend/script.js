const API="http://127.0.0.1:5000";
const $=id=>document.getElementById(id);
async function loadConfig(){
 const c=await (await fetch(`${API}/config`)).json();
 $("city").innerHTML='<option value="">Select city</option>'+Object.keys(c.cities).map(x=>`<option>${x}</option>`).join("");
 $("weather").innerHTML=c.weather.map(x=>`<option>${x}</option>`).join("");
 $("city").addEventListener("change",()=>{$("area").innerHTML='<option value="">Select area</option>'+c.cities[$("city").value].map(x=>`<option>${x}</option>`).join("")});
}
async function loadMetrics(){const m=await (await fetch(`${API}/metrics`)).json();$("r2").textContent=m.R2.toFixed(4);$("rmse").textContent=m.RMSE.toFixed(0);$("maeTop").textContent=m.MAE.toFixed(0)}
async function loadHistory(){const rows=await (await fetch(`${API}/history?limit=12`)).json();$("history").innerHTML=rows.map(r=>`<tr><td><b>${r.area}</b><br><span class="muted">${r.city}</span></td><td>${r.date}<br>${r.time}</td><td>${r.weather}</td><td>${Number(r.predicted_volume).toLocaleString()}</td><td class="status ${r.congestion_level}">${r.congestion_level}</td><td>${r.congestion_score}</td></tr>`).join("")||'<tr><td colspan="6">No predictions yet.</td></tr>'}
$("form").addEventListener("submit",async e=>{e.preventDefault();$("btn").disabled=true;$("btn").textContent="ANALYZING…";$("error").textContent="";
try{const payload={city:$("city").value,area:$("area").value,date:$("date").value,time:$("time").value,weather:$("weather").value,temperature:Number($("temp").value)};
const r=await fetch(`${API}/predict`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});const d=await r.json();if(!r.ok)throw Error(d.error||"Prediction failed");
$("level").textContent=d.congestion_level+" CONGESTION";$("level").className=d.congestion_level;$("score").textContent=d.congestion_score;$("volume").textContent=d.traffic_volume.toLocaleString();$("range").textContent=`${d.prediction_range[0].toLocaleString()}–${d.prediction_range[1].toLocaleString()}`;$("mae").textContent=d.model_mae;$("recommendation").textContent=d.recommendation;await loadHistory()}catch(err){$("error").textContent=err.message}finally{$("btn").disabled=false;$("btn").textContent="ANALYZE TRAFFIC"}});
$("refresh").onclick=loadHistory;
const now=new Date();$("date").value=now.toISOString().slice(0,10);$("time").value=now.toTimeString().slice(0,5);
loadConfig().then(()=>{loadMetrics();loadHistory()}).catch(e=>$("error").textContent="Start the Flask API first.");
