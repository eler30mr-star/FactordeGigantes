// Prueba local REAL del Worker con Wrangler y D1; no contacta Cloudflare remoto ni GitHub.
import assert from "node:assert/strict";
import {randomUUID} from "node:crypto";
const base="http://127.0.0.1:8797";
const token="factor-local-admin-e2e-test-000000000000";
const request=async (path,method="GET",body,credential=token)=>{
 const response=await fetch(base+path,{
  method,
  headers:{"Authorization":"Bearer "+credential,...(body?{"Content-Type":"application/json"}:{})},
  ...(body?{body:JSON.stringify(body)}:{})
 });
 const json=await response.json();
 return {status:response.status,json};
};
const manifest={
 title:"Factor de Gigantes: circuito editorial sin publicación",
 angle:"¿Podemos verificar un expediente completo antes de autorizar un render técnico?",
 format:"short",
 sources:["https://www.sec.gov/edgar/search/","https://www.wipo.int/"],
 segments:[
  {headline:"Problema",voiceover:"El documental exige evidencia para cada afirmación antes de pasar a producción."},
  {headline:"Responsabilidad",voiceover:"Las licencias y revisión humana se comprueban antes de generar una prueba."}
 ]
};
const sample=verified=>({
 title:manifest.title,thesis:manifest.angle,publication_authorized:false,
 sources:[
  {id:"S01",url:manifest.sources[0],publisher:"SEC",accessed_on:"2026-10-20",type:"primaria"},
  {id:"S02",url:manifest.sources[1],publisher:"WIPO",accessed_on:"2026-10-20",type:"primaria"}
 ],
 claims:manifest.segments.map((segment,i)=>({
  id:"C0"+(i+1),segment_index:i+1,text:segment.voiceover,
  evidence:[{source_id:i===0?"S01":"S02",locator:"Documento y página verificados solo en entorno de pruebas",status:verified?"verificada":"pendiente"}],
  reviewed_by:verified?"Revisor de laboratorio":""
 })),
 assets:[{kind:"voz",description:"Solo pista de prueba local, sin licencia comercial acreditada",
          rights_status:verified?"verificado":"pendiente"}]
});
async function main(){
 const unauth=await request("/api/jobs");
 assert.equal(unauth.status,200);
 const noToken=await request("/api/jobs","GET",undefined,"invalid");
 assert.equal(noToken.status,401);
 // Investigación pausada por defecto: no hay gasto ni solicitud GitHub.
 const researchDenied=await request("/api/research","GET",undefined,"invalid");
 assert.equal(researchDenied.status,401);
 const researchList=await request("/api/research");
 assert.equal(researchList.status,200);
 assert.ok(Array.isArray(researchList.json.requests));
 assert.equal(researchList.json.requests.length,0);
 assert.equal(researchList.json.research_paused,true);
 const mustConfirm=await request("/api/research","POST",{topic:"La transformación del sector móvil",confirmed:false});
 assert.equal(mustConfirm.status,409);
 const noResearchGitHub=await request("/api/research","POST",{topic:"La transformación del sector móvil",confirmed:true});
 assert.equal(noResearchGitHub.status,409,"Los investigadores siguen pausados incluso con confirmación");
 assert.equal((await request("/api/research")).json.requests.length,0);
 const creation=await request("/api/jobs","POST",manifest);
 assert.equal(creation.status,201,JSON.stringify(creation));
 const id=creation.json.job.id;
 assert.match(id,/^[0-9a-f-]{36}$/);
 const path="/api/jobs/"+encodeURIComponent(id);
 assert.equal((await request(path+"/dossier")).json.dossier,null);
 assert.equal((await request(path+"/dossier","PUT",sample(false))).status,200);
 assert.equal((await request(path+"/submit","POST",{})).status,200);
 assert.equal((await request(path+"/approve","POST",{confirmed:true})).status,409);
 assert.equal((await request(path+"/dossier/attest","POST",{confirmed:true,reviewer:"Revisor de laboratorio"})).status,409);
 assert.equal((await request(path+"/dossier","PUT",sample(true))).status,200);
 assert.equal((await request(path+"/dossier/attest","POST",{confirmed:true,reviewer:"Revisor de laboratorio"})).status,200);
 assert.equal((await request(path+"/approve","POST",{confirmed:true})).status,200);
 const noGithub=await request(path+"/dispatch","POST",{});
 assert.equal(noGithub.status,503,"No existe token real y nunca debe lanzarse un render externo");
 assert.equal((await request(path)).json.job.status,"approved");
 const changed=await request(path+"/request-changes","POST",{note:"Comprobar de nuevo las licencias antes de enviar"});
 assert.equal(changed.status,200);
 const dossierAfter=(await request(path+"/dossier")).json;
 assert.equal(dossierAfter.attested,false);
 assert.equal((await request(path+"/approve","POST",{confirmed:true})).status,409);
 const audit=await request(path);
 assert.equal(audit.status,200);
 assert.ok(audit.json.events.some(e=>e.action==="dossier_attested"));
 assert.ok(audit.json.events.some(e=>e.action==="changes_requested"));
 console.log("E2E OK: auth, D1 local, evidencias, revisión humana, bloqueo, revocación, auditoría; SIN PUBLICACIÓN.");
}
await main();

