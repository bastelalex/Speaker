export const MODEL_VERSION = '1.0';
export const C = 343;
const rad = x => x * Math.PI / 180;
const deg = x => x * 180 / Math.PI;
export function calculate(input, driver) {
  const {horizontal:h, vertical:v, low:lo, high:hi, columns:nx=1, rows:ny=1, family='single'}=input;
  if (![h,v,lo,hi,nx,ny].every(Number.isFinite)) throw Error('Alle Eingaben müssen endliche Zahlen sein.');
  if (h<10||h>150||v<10||v>150) throw Error('Winkel müssen zwischen 10° und 150° liegen.');
  if (lo<100||hi>24000||lo>=hi) throw Error('Band: 100 ≤ untere < obere Grenze ≤ 24000 Hz.');
  if (![nx,ny].every(n=>Number.isInteger(n)&&n>=1&&n<=12)) throw Error('Zellzahlen müssen ganzzahlig zwischen 1 und 12 liegen.');
  if (!driver || !(driver.throat_mm>0)) throw Error('Gültigen Treiber auswählen.');
  const d=driver.throat_mm/1000, wavelength=C/lo;
  const w=Math.max(d+0.01,0.603*wavelength/Math.sin(rad(h/2)));
  const height=Math.max(d+0.01,0.603*wavelength/Math.sin(rad(v/2)));
  const length=Math.max((w-d)/(2*Math.tan(rad(h/2))),(height-d)/(2*Math.tan(rad(v/2))));
  const area=Math.PI*d*d/4, mouth=w*height;
  const compatible=lo>=Math.max(driver.crossover_hz,driver.range_hz[0])&&hi<=driver.range_hz[1];
  const warnings=[];
  if(!compatible) warnings.push('Keine positive Bandvorauswahl: Frequenzband oder Trenn-Untergrenze passt nicht zum Treiber.');
  warnings.push(driver.crossover_status);
  warnings.push('Aperturmodell bei −6 dB; keine simulierte oder gemessene Richtwirkung. Pegel und Filter sind nicht freigegeben.');
  if(family!=='single') warnings.push('Für diese Familie gelten die Außenmaße nur als Referenzhülle. Innenkörper, Kammern und Kanalwege sind noch nicht konstruiert.');
  const cells=family==='multi'||family==='poly';
  const cols=cells?nx:1, rows=cells?ny:1;
  const cellwidth=w/cols, cellheight=height/rows;
  const modal=C/(2*Math.max(cellwidth,cellheight));
  if(cells) warnings.push('Zellraster ohne Wandstärken und Verteiler. Keine Zellstrahlbreiten aus Winkel/Zellzahl ableiten. Ein Treiber, keine Leistungsaddition.');
  if(Math.max(w,height,length)>1) warnings.push('Mindestens ein Hüllmaß über 1 m: Zielband, Winkel und Bauraum gemeinsam überarbeiten.');
  return {model_version:MODEL_VERSION,date:'2026-11-12',input:{...input,columns:cols,rows},driver_id:driver.id,source:driver.source,compatible,
    throat_mm:driver.throat_mm,throat_area_mm2:area*1e6,mouth_width_mm:w*1000,mouth_height_mm:height*1000,length_mm:length*1000,
    wall_horizontal_deg:deg(2*Math.atan((w-d)/(2*length))),wall_vertical_deg:deg(2*Math.atan((height-d)/(2*length))),
    path_budget_mm:C/(8*hi)*1000,spacing_check_mm:C/(2*hi)*1000,cell_width_mm:cellwidth*1000,cell_height_mm:cellheight*1000,
    rectangular_mode_check_hz:modal,comparison_exponential_cutoff_hz:Math.log(mouth/area)/length*C/(4*Math.PI),warnings};
}
export function chamber(volume_cm3, area_mm2, effective_length_mm) {
  if(![volume_cm3,area_mm2,effective_length_mm].every(v=>Number.isFinite(v)&&v>0)) throw Error('Kammerparameter müssen positiv und endlich sein.');
  const rho=1.204,V=volume_cm3*1e-6,S=area_mm2*1e-6,l=effective_length_mm/1000;
  const compliance=V/(rho*C*C),inertance=rho*l/S;
  return {compliance_m3_per_pa:compliance,inertance_pa_s2_per_m3:inertance,helmholtz_hz:1/(2*Math.PI*Math.sqrt(compliance*inertance))};
}
