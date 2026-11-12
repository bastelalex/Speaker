/* Dependency-free, orthographic triangle renderer. Own meshes, no remote assets. */
(()=>{'use strict';
const library=window.SPEAKER_MODELS;if(!library)return;
const $=id=>document.getElementById(id),dialog=$('viewer'),canvas=$('stage'),ctx=canvas.getContext('2d');
let current=null,yaw=-32,pitch=25,zoom=1,pointer=null;
const palette=[[36,96,103],[80,155,151],[151,217,188],[227,156,83]];
const dot=(a,b)=>a.reduce((sum,v,i)=>sum+v*b[i],0),sub=(a,b)=>a.map((v,i)=>v-b[i]);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const unit=a=>{const n=Math.hypot(...a)||1;return a.map(v=>v/n);};
function render(){
 if(!current||!dialog.open)return;
 const model=library[current],width=canvas.clientWidth,height=canvas.clientHeight,ratio=Math.min(window.devicePixelRatio||1,2);
 canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);ctx.setTransform(ratio,0,0,ratio,0,0);ctx.fillStyle='#10282d';ctx.fillRect(0,0,width,height);
 const a=yaw*Math.PI/180,b=pitch*Math.PI/180,u=[Math.cos(a),0,Math.sin(a)],v=[-Math.sin(a)*Math.sin(b),Math.cos(b),Math.cos(a)*Math.sin(b)],eye=cross(u,v);
 const points=model.vertices.map(p=>[dot(p,u),-dot(p,v),dot(p,eye)]);
 let xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;
 for(const p of points){xmin=Math.min(xmin,p[0]);xmax=Math.max(xmax,p[0]);ymin=Math.min(ymin,p[1]);ymax=Math.max(ymax,p[1]);}
 const scale=Math.min((width-65)/(xmax-xmin||1),(height-45)/(ymax-ymin||1))*zoom,cx=(xmin+xmax)/2,cy=(ymin+ymax)/2;
 const light=unit([-.4,.7,.8]),cut=$('cutaway').checked;
 const faces=model.faces.map(f=>({f,z:(points[f[0]][2]+points[f[1]][2]+points[f[2]][2])/3})).sort((a,b)=>a.z-b.z);
 for(const {f} of faces){
  const [i,j,k,material]=f;
  if(cut&&material!==3&&(model.vertices[i][0]+model.vertices[j][0]+model.vertices[k][0])/3<0)continue;
  const normal=unit(cross(sub(model.vertices[j],model.vertices[i]),sub(model.vertices[k],model.vertices[i])));
  if(!cut&&dot(normal,eye)<=0)continue;
  const brightness=.42+.58*Math.abs(dot(normal,light)),color=palette[material].map(v=>Math.round(v*brightness));
  ctx.fillStyle=`rgb(${color.join(',')})`;ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=.35;ctx.beginPath();
  [i,j,k].forEach((index,n)=>{const p=points[index],x=width/2+(p[0]-cx)*scale,y=height/2+(p[1]-cy)*scale;n?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.closePath();ctx.fill();ctx.stroke();
 }
 ctx.font='12px system-ui';ctx.fillStyle='#b9d2c3';ctx.fillText(cut?'Halbschnitt · ungeprüfte Konzeptgeometrie':'Ungeprüfte Konzeptgeometrie · Maße in mm',18,height-14);
 $('yaw').value=yaw;$('pitch').value=pitch;
}
function open(id){if(!library[id])return;current=id;yaw=-32;pitch=25;zoom=1;$('cutaway').checked=false;$('model-title').textContent=library[id].title;$('download-obj').href='../models/'+id+'.obj';if(!dialog.open)dialog.showModal();render();canvas.focus();}
document.querySelectorAll('[data-open]').forEach(b=>b.addEventListener('click',()=>open(b.dataset.open)));
$('close').onclick=()=>dialog.close();dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelectorAll('.card').forEach(c=>c.hidden=b.dataset.filter!=='all'&&c.dataset.group!==b.dataset.filter);}));
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{const view=b.dataset.view;[yaw,pitch]=view==='front'?[0,0]:view==='side'?[-90,0]:[-32,25];zoom=1;render();});
// A front camera looks towards the +z mouth, not down the x axis.
document.querySelector('[data-view="front"]').onclick=()=>{yaw=0;pitch=0;zoom=1;render();};
// Projection basis u=(cos yaw,0,sin yaw), v has the vertical y component.
$('yaw').oninput=e=>{yaw=+e.target.value;render();};$('pitch').oninput=e=>{pitch=+e.target.value;render();};$('cutaway').onchange=render;
canvas.onpointerdown=e=>{pointer={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);};
canvas.onpointermove=e=>{if(!pointer||pointer.id!==e.pointerId)return;yaw=((yaw+(e.clientX-pointer.x)*.45+180)%360+360)%360-180;pitch=Math.max(-80,Math.min(80,pitch+(e.clientY-pointer.y)*.35));pointer.x=e.clientX;pointer.y=e.clientY;render();};
canvas.onpointerup=canvas.onpointercancel=()=>{pointer=null;};
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.4,Math.min(3,zoom*Math.exp(-e.deltaY*.001)));render();},{passive:false});
canvas.onkeydown=e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','='].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=5;if(e.key==='ArrowRight')yaw+=5;if(e.key==='ArrowUp')pitch-=5;if(e.key==='ArrowDown')pitch+=5;if(e.key==='+'||e.key==='=')zoom*=1.1;if(e.key==='-')zoom/=1.1;pitch=Math.max(-80,Math.min(80,pitch));yaw=((yaw+180)%360+360)%360-180;zoom=Math.max(.4,Math.min(3,zoom));render();};
function stl(id){
 const model=library[id],lines=['solid speaker_'+id];
 for(const [i,j,k] of model.faces){const a=model.vertices[i],b=model.vertices[j],c=model.vertices[k],n=unit(cross(sub(b,a),sub(c,a)));lines.push('facet normal '+n.map(v=>v.toPrecision(8)).join(' '),'outer loop',...[a,b,c].map(p=>'vertex '+p.map(v=>v.toFixed(6)).join(' ')),'endloop','endfacet');}
 lines.push('endsolid speaker_'+id);const url=URL.createObjectURL(new Blob([lines.join('\n')+'\n'],{type:'model/stl'})),a=document.createElement('a');a.href=url;a.download=id+'-concept-mm.stl';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
}
document.querySelectorAll('[data-stl]').forEach(b=>b.onclick=()=>stl(b.dataset.stl));$('download-stl').onclick=()=>{if(current)stl(current);};
window.addEventListener('resize',render);
})();
