import test from "node:test";
import assert from "node:assert/strict";
import {
 cloneDossier,nextEditorialId,addEditorialClaim,deleteEditorialClaim,
 addEditorialEvidence,addEditorialAsset,deleteEditorialAsset,deleteEditorialSource
} from "../public/dossier-editor.js";
import {validateDossier} from "../src/editorial.mjs";
const manifest={
 title:"Factor de Gigantes: piloto editorial",
 angle:"¿Cómo respaldar con documentos originales cada afirmación del guion?",
 sources:["https://www.sec.gov/edgar/search/","https://www.wipo.int/"],
 segments:[
  {headline:"Origen",voiceover:"Esta afirmación técnica de prueba debe verificarse editorialmente."},
  {headline:"Consecuencias",voiceover:"Esta segunda afirmación también debe acreditarse con fuentes reales."},
 ]};
function initial(){
 return {
  title:manifest.title,thesis:manifest.angle,publication_authorized:false,
  sources:[
   {id:"S01",url:manifest.sources[0],publisher:"SEC",accessed_on:"2026-10-20",type:"primaria"},
   {id:"S02",url:manifest.sources[1],publisher:"WIPO",accessed_on:"2026-10-20",type:"primaria"}
  ],
  claims:manifest.segments.map((s,i)=>({
   id:"C0"+(i+1),segment_index:i+1,text:s.voiceover,reviewed_by:"",
   evidence:[{source_id:"S01",locator:"Informe y sección pendiente",status:"pendiente"}]
  })),
  assets:[{kind:"voz",description:"Referencia vocal aprobada, licencia comercial pendiente",rights_status:"pendiente"}]
 };
}
test("crear afirmaciones adicionales nunca las marca verificadas",()=>{
 const d=initial();
 const c=addEditorialClaim(d,1);
 assert.equal(c.segment_index,1);
 assert.equal(c.id,"C03");
 assert.equal(c.evidence[0].status,"pendiente");
 assert.equal(c.reviewed_by,"");
 assert.equal(validateDossier(d,manifest).structurally_complete,false);
});
test("evitar dejar escenas sin evidencia y mantener máximo de identificadores",()=>{
 const d=initial();
 assert.throws(()=>deleteEditorialClaim(d,"C01"),/escena/);
 const added=addEditorialClaim(d,1);
 deleteEditorialClaim(d,added.id);
 assert.equal(d.claims.length,2);
 assert.equal(nextEditorialId([{id:"C01"},{id:"C03"}],"C"),"C02");
});
test("añadir evidencia utiliza una fuente diferente y empieza pendiente",()=>{
 const d=initial();
 addEditorialEvidence(d,d.claims[0]);
 assert.deepEqual(d.claims[0].evidence.map(x=>x.source_id),["S01","S02"]);
 assert.equal(d.claims[0].evidence[1].status,"pendiente");
 assert.throws(()=>addEditorialEvidence(d,d.claims[0]),/fuentes/);
});
test("nunca elimina única voz ni fuente necesaria para el guion",()=>{
 const d=initial();
 assert.throws(()=>deleteEditorialAsset(d,0),/voz/);
 assert.throws(()=>deleteEditorialSource(d,"S01",manifest.sources),/guion/);
 d.sources.push({id:"S03",url:"https://www.example.org/",publisher:"Ejemplo",
                 accessed_on:"2026-10-20",type:"secundaria"});
 deleteEditorialSource(d,"S03",manifest.sources);
 assert.equal(d.sources.length,2);
});
test("recurso nuevo no obtiene derechos automáticamente y la clonación no muta original",()=>{
 const d=initial();
 const copy=cloneDossier(d);
 const asset=addEditorialAsset(copy);
 assert.equal(asset.rights_status,"pendiente");
 copy.claims[0].text="Una afirmación distinta pero pendiente de verificación manual.";
 assert.notEqual(copy.claims[0].text,d.claims[0].text);
 deleteEditorialAsset(copy,1);
 assert.equal(copy.assets.length,1);
});
