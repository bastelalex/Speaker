import {calculate,chamber} from './core.mjs';
const drivers=JSON.parse(document.getElementById('drivers').textContent);
const sources=JSON.parse(document.getElementById('sources').textContent);
const $=s=>document.querySelector(s),form=$('#inputs');let result;
form.addEventListener('submit',event=>event.preventDefault());
$('#chamber').addEventListener('submit',event=>event.preventDefault());
const fmt=(v,n=1)=>v.toLocaleString('de-DE',{maximumFractionDigits:n});
$('#driver').innerHTML=drivers.map(d=>`<option value="${d.id}">${d.brand} ${d.model} · ${d.throat_mm} mm · ${d.impedance_ohm} Ω</option>`).join('');
const names={single:'Einzel-Waveguide',rocket:'Raketen-Ringkanal',axe:'Axtkopf-Zweikanal',multi:'Multicell',poly:'Polycell-Konzept',manifold:'Mehrtreiber-Manifold'};
function values(){const f=new FormData(form);return {horizontal:+f.get('horizontal'),vertical:+f.get('vertical'),low:+f.get('low'),high:+f.get('high'),columns:+f.get('columns'),rows:+f.get('rows'),family:f.get('family')};}
function draw(r){
  const scale=430/Math.max(r.mouth_width_mm,r.mouth_height_mm),w=r.mouth_width_mm*scale,h=r.mouth_height_mm*scale;
  const x=300-w/2,y=255-h/2;
  let cells='';for(let i=1;i<r.input.columns;i++) cells+=`<path d="M ${x+w*i/r.input.columns} ${y} v ${h}"/>`;
  for(let i=1;i<r.input.rows;i++)cells+=`<path d="M ${x} ${y+h*i/r.input.rows} h ${w}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 560" role="img" aria-label="Schematische Frontansicht der Referenzhülle"><rect width="600" height="560" fill="#10282d"/><g stroke="#74d8bd" stroke-width="2" fill="none"><rect x="${x}" y="${y}" width="${w}" height="${h}"/>${cells}<circle cx="300" cy="255" r="${r.throat_mm*scale/2}" stroke-dasharray="4 4"/></g><g fill="#e8f2ee" text-anchor="middle" font-family="sans-serif" font-size="17"><text x="300" y="28">${names[r.input.family]} · Frontansicht</text><text x="300" y="500">${fmt(r.mouth_width_mm)} × ${fmt(r.mouth_height_mm)} mm</text><text x="300" y="528">Referenzhülle · Innengeometrie nicht dargestellt</text></g></svg>`;
}
function update(){try{
  const input=values(),d=drivers.find(d=>d.id===$('#driver').value);result=calculate(input,d);
  $('#error').textContent='';$('#export').disabled=false;$('#svgexport').disabled=false;
  $('#status').textContent=result.compatible?'Banddaten passen · akustischer Nachweis offen':'Treiber passt nicht zum eingegebenen Band';$('#status').className=result.compatible?'status':'status bad';
  const entries=[['Mundbreite',result.mouth_width_mm,'mm'],['Mundhöhe',result.mouth_height_mm,'mm'],['Hülllänge',result.length_mm,'mm'],['Halsfläche',result.throat_area_mm2,'mm²'],['45°-Wegbudget',result.path_budget_mm,'mm'],['λ/2-Abstandscheck',result.spacing_check_mm,'mm']];
  $('#metrics').innerHTML=entries.map(([n,v,u])=>`<div><small>${n}</small><strong>${fmt(v,2)} <span>${u}</span></strong></div>`).join('');
  $('#drawing').innerHTML=draw(result);
  $('#details').textContent=`Tatsächliche Wandwinkel der Hülle: ${fmt(result.wall_horizontal_deg)}° H / ${fmt(result.wall_vertical_deg)}° V. Zellreferenz: ${fmt(result.cell_width_mm)} × ${fmt(result.cell_height_mm)} mm. Idealer Rechteckkanal-Querformcheck: ${fmt(result.rectangular_mode_check_hz,0)} Hz. Äquivalentes Exponential-fc (nur Vergleich): ${fmt(result.comparison_exponential_cutoff_hz,0)} Hz.`;
  $('#warnings').replaceChildren(...result.warnings.map(t=>{const li=document.createElement('li');li.textContent=t;return li;}));
  const source=sources.find(s=>s.id===d.source);$('#driverdata').innerHTML=`<b>${d.brand} ${d.model}</b><p>${d.range_hz.join('–')} Hz · Trenn-/Projektgrenze ${d.crossover_hz} Hz · ${d.impedance_ohm} Ω</p><p>AES: ${d.aes_w??'unbekannt'} ${d.aes_w?'W':''} · Program: ${d.program_w} W (Bedingungen siehe Quelle)</p><p>Empfindlichkeit: ${d.sensitivity_db} dB. ${d.sensitivity_note}</p><a href="${source.url}" target="_blank" rel="noopener">${source.id} · Herstellerquelle öffnen ↗</a>`;
}catch(e){result=null;$('#error').textContent=e.message;$('#export').disabled=true;$('#svgexport').disabled=true;$('#status').textContent='Keine gültige Berechnung';$('#metrics').replaceChildren();$('#drawing').replaceChildren();$('#details').textContent='';$('#warnings').replaceChildren();$('#driverdata').replaceChildren();}}
form.addEventListener('input',update);
function download(text,type,name){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('#export').onclick=()=>{if(result)download(JSON.stringify({...result,driver:drivers.find(d=>d.id===result.driver_id),assumptions:['c=343 m/s','gleichmäßig belegte Apertur −6 dB','keine akustische Simulation','ein Treiber pro Referenzhorn']},null,2),'application/json','waveguide-entwurf.json');};
$('#svgexport').onclick=()=>{if(result)download(draw(result),'image/svg+xml','waveguide-referenz.svg');};
function updateChamber(){try{const r=chamber(+$('#volume').value,+$('#area').value,+$('#neck').value);$('#chamber-result').textContent=`fH ≈ ${fmt(r.helmholtz_hz)} Hz · Ca = ${r.compliance_m3_per_pa.toExponential(3)} m³/Pa · Ma = ${fmt(r.inertance_pa_s2_per_m3)} Pa·s²/m³. Ideales Lernmodell, keine interne Treiberkammer.`;}catch(e){$('#chamber-result').textContent=e.message;}}
$('#chamber').addEventListener('input',updateChamber);update();updateChamber();
