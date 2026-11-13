// Local contour editor for the S3 geometry. Coordinates are in millimetres.
const sampleCount=32;
const reliefStart=7, reliefEnd=130;
const MAX_RELIEF=18;
const referenceRadii=Array.from({length:sampleCount},(_,i)=>{
  const a=2*Math.PI*i/sampleCount;
  return 1+.17*Math.cos(5*a+.35)+.071*Math.sin(3*a-.5)+.035*Math.sin(2*a);
});
const contours={
  falte:{label:'Falte · synthetisch',radii:referenceRadii},
  vierblatt:{label:'Vierblatt · synthetisch',radii:referenceRadii.map((_,i)=>{
    const a=2*Math.PI*i/sampleCount;
    return 1+.24*Math.cos(4*a)+.05*Math.sin(3*a+.32);
  })},
  wirbel:{label:'Wirbel · synthetisch',radii:referenceRadii.map((_,i)=>{
    const a=2*Math.PI*i/sampleCount;
    return 1+.18*Math.sin(7*a+1.35*Math.sin(2*a))+.09*Math.cos(3*a);
  })}
};
let solanalMode='falte', relief=76, customProfile=null;
const solanal=$('#solanal');
const profileInput=$('#profile-file');
const profileMessage=$('#profile-message');
const reliefSlider=$('#relief');
const profileSelect=$('#profile');
const layerMat=new THREE.MeshStandardMaterial({color:'#e5c39c',roughness:.61,metalness:.04,envMapIntensity:.8});
layerMat.onBeforeCompile=shader=>{
  shader.vertexShader='varying vec3 hornLocal;\n'+shader.vertexShader.replace(
    '#include <begin_vertex>','#include <begin_vertex>\nhornLocal=position;');
  shader.fragmentShader='varying vec3 hornLocal;\n'+shader.fragmentShader.replace(
    '#include <color_fragment>',`#include <color_fragment>
      float d=max(0.,-hornLocal.z);
      float layer=d/2.72+.035*sin(hornLocal.x*.017)+.018*sin(hornLocal.y*.037);
      float footprint=max(.012,fwidth(layer)*.7);
      float distance=abs(fract(layer+.5)-.5);
      float glue=(1.-smoothstep(.050-footprint,.066+footprint,distance))
                 *(1.-smoothstep(.12,.45,footprint));
      float grain=.94+.048*cos(hornLocal.x*.072+hornLocal.y*.025)
                  +.024*sin(hornLocal.x*.278+hornLocal.y*.071);
      float veneer=.98+.065*sin(floor(layer+.5)*2.74);
      vec3 edge=mix(vec3(1.10,1.0,.91)*veneer,vec3(.36,.205,.115),glue*.73);
      vec3 face=vec3(1.05,.97,.85)*grain;
      float shade=1.-.70*smoothstep(13.,240.,d);
      diffuseColor.rgb*=mix(face,edge,smoothstep(.2,3.,d))*shade;
    `);
};
layerMat.customProgramCacheKey=()=> 'solanal-plywood';

for(const [key,{label}] of Object.entries(contours))profileSelect.add(new Option(label,key));

function parseProfile(input){
  const values=input?.radien;
  if(input?.version!==1 || !Array.isArray(values) || values.length!==sampleCount ||
     values.some(v=>typeof v!=='number'||!Number.isFinite(v)||v<=0||v>1e6)){
    throw Error('Benötigt werden Version 1 und genau 32 positive Zahlen unter „radien“.');
  }
  const average=values.reduce((sum,v)=>sum+v,0)/sampleCount;
  if(Math.min(...values)/average<.20 || Math.max(...values)/average>2.5){
    throw Error('Die Radien weichen zu stark voneinander ab. Bitte Mittelpunkt und Reihenfolge prüfen.');
  }
  return values.slice();
}

function radialOffsets(values){
  let valuesSmoothed=values.slice();
  for(let pass=0;pass<2;pass++){
    const row=valuesSmoothed;
    valuesSmoothed=row.map((v,i)=>(row[(i-1+sampleCount)%sampleCount]+2*v+row[(i+1)%sampleCount])/4);
  }
  const mean=valuesSmoothed.reduce((sum,v)=>sum+v,0)/sampleCount;
  const centered=valuesSmoothed.map(v=>v-mean);
  const scale=Math.max(mean*.14,...centered.map(Math.abs));
  return centered.map(v=>v/scale);
}

function valueAt(samples,a){
  const t=((a/(2*Math.PI)+1)%1)*sampleCount,i=Math.floor(t),w=t-i;
  const at=k=>samples[(i+k+sampleCount)%sampleCount];
  const p=at(0), q=at(1), dp=(q-at(-1))/2, dq=(at(2)-p)/2;
  return THREE.MathUtils.clamp(p+w*(dp+w*(3*(q-p)-2*dp-dq+w*(2*(p-q)+dp+dq))),-1,1);
}

function morphSolanal(){
  const current=signature('SL'), mesh=current.group.children[0];
  const profile=solanalMode==='custom'?customProfile:contours[solanalMode].radii;
  const samples=radialOffsets(profile);
  const intensity=MAX_RELIEF*relief/100;
  const coords=mesh.geometry.attributes.position;
  const base=mesh.userData.base;
  for(let i=0;i<coords.count;i++){
    const k=i*3, x=base[k], y=base[k+1], z=base[k+2], d=-z;
    let shift=0;
    if(d>reliefStart&&d<reliefEnd){
      const t=(d-reliefStart)/(reliefEnd-reliefStart);
      const a=Math.atan2(y/123,x/258);
      const radial=Math.min(1,Math.hypot(x/258,y/123)/.21);
      shift=intensity*Math.sin(Math.PI*t)**2*valueAt(samples,a)*radial;
    }
    coords.setXYZ(i,x,y,z-shift);
  }
  coords.needsUpdate=true;
  smoothSolanal(mesh);
  mesh.geometry.computeBoundingSphere();
}

function smoothSolanal(mesh){
  // Compute normals on the original connected topology, then keep hard creases.
  const flat=mesh.geometry, topology=mesh.userData.topology;
  flat.computeVertexNormals();
  creaseNormals(topology,flat);
}

function saveFile(name,content,type){
  const url=URL.createObjectURL(new Blob([content],{type}));
  const a=document.createElement('a');a.href=url;a.download=name;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1500);
}

function exportSolanal(){
  const vertices=signature('SL').group.children[0].geometry.attributes.position;
  const count=vertices.count/3;
  const file=new DataView(new ArrayBuffer(84+count*50));
  const header=new TextEncoder().encode('restless.audio SOLANAL | mm | experimental horn');
  new Uint8Array(file.buffer).set(header);
  file.setUint32(80,count,true);
  function point(i){return new THREE.Vector3(vertices.getX(i),-vertices.getZ(i),vertices.getY(i));}
  for(let i=0;i<count;i++){
    let pos=84+i*50;
    const a=point(i*3),b=point(i*3+1),c=point(i*3+2);
    const normal=b.clone().sub(a).cross(c.clone().sub(a)).normalize();
    for(const v of [normal,a,b,c]){
      for(const n of [v.x,v.y,v.z]){file.setFloat32(pos,n,true);pos+=4;}
    }
  }
  saveFile('SOLANAL_'+solanalMode+'.stl',file.buffer,'model/stl');
}

profileInput.addEventListener('change',async ()=>{
  const file=profileInput.files[0];
  if(!file)return;
  try{
    if(file.size>10000)throw Error('Die Konturdatei darf höchstens 10 kB groß sein.');
    customProfile=parseProfile(JSON.parse(await file.text()));
    if(!profileSelect.querySelector('[value=custom]'))profileSelect.add(new Option('Eigene Kontur','custom'));
    solanalMode='custom';
    profileSelect.value=solanalMode;
    profileMessage.textContent='Eigene Kontur für diese Sitzung geladen.';
    morphSolanal();sync();
  }catch(err){
    profileMessage.textContent=err instanceof SyntaxError?'Die Datei enthält kein gültiges JSON.':err.message;
  }finally{profileInput.value='';}
});
profileSelect.addEventListener('change',()=>{
  solanalMode=profileSelect.value;morphSolanal();sync();
});
reliefSlider.addEventListener('input',()=>{
  relief=Number(reliefSlider.value);$('#relief-value').value=relief+' %';morphSolanal();sync();
});
$('#example').addEventListener('click',()=>{
  const example={version:1,radien:referenceRadii.map(v=>Math.round(1000*v)/1000)};
  saveFile('SOLANAL_Konturvorlage.json',JSON.stringify(example,null,2),'application/json');
});
$('#export').addEventListener('click',exportSolanal);
