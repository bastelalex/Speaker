import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {calculate,chamber} from '../configurator/core.mjs';
const ds=JSON.parse(readFileSync(new URL('../data/drivers.json',import.meta.url)));
const base={horizontal:90,vertical:40,low:1200,high:18000,columns:3,rows:2,family:'multi'};
test('Rechenbeispiel: Apertur, Geometrie und Wegbudget',()=>{
 const r=calculate(base,ds[0]); assert.ok(Math.abs(r.mouth_width_mm-243.75)<1);assert.ok(Math.abs(r.mouth_height_mm-503.95)<1);assert.ok(Math.abs(r.length_mm-657.4)<2);assert.ok(Math.abs(r.path_budget_mm-2.38194)<0.001);assert.equal(r.compatible,true);
 assert.ok(Math.abs(r.wall_vertical_deg-40)<1e-9);assert.ok(r.wall_horizontal_deg<90);
});
test('Zu kleines Bandende und falsche Trennung sperren die Vorauswahl',()=>{
 assert.equal(calculate({...base,high:20000},ds[0]).compatible,false);
 assert.equal(calculate({...base,low:500},ds[0]).compatible,false);
 assert.equal(calculate({...base,low:500},ds[3]).compatible,false);
});
test('Skalierung: doppelte Frequenz halbiert Apertur',()=>{const a=calculate(base,ds[0]),b=calculate({...base,low:2400},ds[0]);assert.ok(Math.abs(a.mouth_width_mm/2-b.mouth_width_mm)<1e-9);});
test('Ungültige Werte und Zellzahlen werden abgelehnt',()=>{
 for(const change of [{low:NaN},{high:100},{horizontal:0},{vertical:180},{columns:1.5},{rows:0}]) assert.throws(()=>calculate({...base,...change},ds[0]));
});
test('Zellraster nur für Multicell und Polycell; genau ein Treiber',()=>{const r=calculate({...base,family:'rocket'},ds[1]);assert.equal(r.input.columns,1);assert.equal(r.input.rows,1);});
test('Kammer: analytische Helmholtz-Referenz und Volumenskalierung',()=>{
 const a=chamber(10,100,20),b=chamber(40,100,20);assert.ok(Math.abs(a.helmholtz_hz-1220.68)<1);assert.ok(Math.abs(b.helmholtz_hz-a.helmholtz_hz/2)<1e-9);assert.throws(()=>chamber(0,100,20));assert.throws(()=>chamber(Infinity,100,20));
});
