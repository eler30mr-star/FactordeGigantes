import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/worker.js";
import {sourceUrl,validateDossier} from "../src/editorial.mjs";

const manifest = {
 title:"Factor de Gigantes - Documental de prueba",
 angle:"¿Qué pruebas respaldan el relato de una transformación tecnológica?",
 format:"short",
 sources:["https://www.sec.gov/edgar/search/","https://www.wipo.int/"],
 segments:[
   {headline:"Contexto",voiceover:"El primer bloque se usa solo para comprobar el motor documental."},
   {headline:"Impacto",voiceover:"El segundo bloque mantiene la revisión y la seguridad de origen."}
 ]
};
const sample=()=>({
  title:manifest.title,thesis:manifest.angle,publication_authorized:false,
  sources:[
   {id:"S01",url:manifest.sources[0],publisher:"SEC",accessed_on:"2026-10-20",type:"primaria"},
   {id:"S02",url:manifest.sources[1],publisher:"WIPO",accessed_on:"2026-10-20",type:"primaria"}
  ],
  claims:[
    {id:"C01",text:"Afirmación experimental para el ensayo documental interno.",
     evidence:[{source_id:"S01",locator:"Informe, sección y página por verificar",status:"pendiente"}],
     reviewed_by:""}
  ],
  assets:[{kind:"voz",description:"Narración del documental sin publicar",rights_status:"pendiente"}]
});
function approved() {
  const x=sample();
  x.claims[0].evidence[0].locator="Documento de prueba, página 4";
  x.claims[0].evidence[0].status="verificada";
  x.claims[0].reviewed_by="Responsable editorial de pruebas";
  x.assets[0].rights_status="verificado";
  return x;
}

class DB {
  constructor(){
    this.dossiers=new Map();
    this.jobs=new Map();
    this.events=[];
    this.jobs.set("job-one",{id:"job-one",title:manifest.title,format:"short",status:"draft",
       manifest_json:JSON.stringify(manifest),review_note:"",last_error:"",
       created_at:"2026-10-20",updated_at:"2026-10-20"});
  }
  prepare(sql) {
    const db=this;
    return {params:[],
      bind(...args){this.params=args;return this},
      async first(){
        const p=this.params;
        if(sql.includes("FROM editorial_dossiers"))return db.dossiers.get(p[0]) || null;
        if(sql.includes("FROM jobs"))return db.jobs.get(p[0]) || null;
        throw Error("Unknown first statement "+sql);
      },
      async run(){
        const p=this.params;
        if(sql.startsWith("INSERT INTO editorial_dossiers")) {
          db.dossiers.set(p[0],{dossier_json:p[1],editor_attested:0,editor_name:"",attested_at:null});return {};
        }
        if(sql.startsWith("UPDATE editorial_dossiers")) {
          const d=db.dossiers.get(p[p.length-1]);
          if(d) {
            if(sql.includes("editor_attested=1")){d.editor_attested=1;d.editor_name=p[0];d.attested_at="now";}
            else{d.editor_attested=0;d.editor_name="";d.attested_at=null;}
          }
          return {};
        }
        if(sql.startsWith("INSERT INTO events")){db.events.push({id:p[0],action:p[1]});return {}}
        if(sql.startsWith("UPDATE jobs SET status")){const j=db.jobs.get(p[3]);j.status=p[0];j.review_note=p[1];j.last_error=p[2];return {}}
        if(sql.startsWith("UPDATE jobs SET title")){const j=db.jobs.get(p[3]);j.title=p[0];j.format=p[1];j.manifest_json=p[2];return {}}
        throw Error("Unknown run statement "+sql);
      },
      async all(){
        if(sql.includes("FROM events"))return {results:[]};
        if(sql.includes("FROM jobs"))return {results:[...db.jobs.values()]};
        throw Error("Unknown all statement "+sql);
      }
    };
  }
}
const TOKEN="a".repeat(32);
const url="https://factor-de-gigantes.test";
const make=(path, method="GET",body,credentials=TOKEN)=>
  new Request(url+path,{method, headers:{authorization:"Bearer "+credentials, ...(body ? {"Content-Type":"application/json"} : {})},
    ...(body?{body:JSON.stringify(body)}:{})});
async function api(env, path,method="GET",body,credentials=TOKEN){
  const r=await worker.fetch(make(path,method,body,credentials),env);
  return {status:r.status,body:await r.json()};
}
const env=()=>({DB:new DB(),ADMIN_TOKEN:TOKEN,RENDERER_TOKEN:"r".repeat(32),
  GITHUB_REPO:"eler30mr-star/FactordeGigantes",GITHUB_DISPATCH_TOKEN:"G".repeat(32)});

test("el contrato editorial no presume veracidad y exige voz y URLs seguras",()=>{
  assert.equal(validateDossier(sample(),manifest).structurally_complete,false);
  assert.equal(validateDossier(approved(),manifest).structurally_complete,true);
  assert.equal(sourceUrl("https://www.wipo.int/"),"https://www.wipo.int/");
  for(const url of ["http://localhost","https://user:pass@example.com","https://127.0.0.1/private"]){
    assert.throws(()=>sourceUrl(url));
  }
  const noVoice=approved();noVoice.assets[0].kind="video";
  assert.throws(()=>validateDossier(noVoice,manifest),/voz/);
  const outOfManifest=approved();outOfManifest.sources[0].url="https://www.example.org/";
  assert.throws(()=>validateDossier(outOfManifest,manifest),/guion/);
});

test("el expediente no se lee sin token y no se acredita incompleto",async()=>{
  const e=env(), p="/api/jobs/job-one/dossier";
  assert.equal((await api(e,p,"GET",undefined,"invalid")).status,401);
  assert.equal((await api(e,p)).body.attested,false);
  assert.equal((await api(e,p,"PUT",sample())).status,200);
  assert.equal((await api(e,p+"/attest","POST",{confirmed:true,reviewer:"Responsable"})).status,409);
  assert.equal((await api(e,"/api/jobs/job-one/submit","POST",{})).status,200);
  assert.equal((await api(e,"/api/jobs/job-one/approve","POST",{confirmed:true})).status,409);
  assert.equal((await api(e,p+"/attest","POST",{confirmed:true,reviewer:"Responsable"})).status,409);
  assert.equal((await api(e,p,"PUT",approved())).status,200);
  assert.equal((await api(e,p+"/attest","POST",{confirmed:true,reviewer:"Responsable"})).status,200);
  assert.equal((await api(e,"/api/jobs/job-one/approve","POST",{confirmed:true})).status,200);
  assert.equal(e.DB.jobs.get("job-one").status,"approved");
});

test("editar expediente invalida acreditación; pedir cambios revoca aprobación",async()=>{
  const e=env(), p="/api/jobs/job-one/dossier";
  await api(e,p,"PUT",approved());
  await api(e,"/api/jobs/job-one/submit","POST",{});
  await api(e,p+"/attest","POST",{confirmed:true,reviewer:"Responsable"});
  const changed=sample();
  assert.equal((await api(e,p,"PUT",changed)).status,200);
  assert.equal(e.DB.dossiers.get("job-one").editor_attested,0);
  assert.equal((await api(e,"/api/jobs/job-one/approve","POST",{confirmed:true})).status,409);
  await api(e,p,"PUT",approved());
  await api(e,p+"/attest","POST",{confirmed:true,reviewer:"Responsable"});
  await api(e,"/api/jobs/job-one/approve","POST",{confirmed:true});
  assert.equal((await api(e,"/api/jobs/job-one/request-changes","POST",{note:"Corregir afirmación sobre licencias"})).status,200);
  assert.equal(e.DB.dossiers.get("job-one").editor_attested,0);
});

test("despacho a GitHub bloquea el expediente revocado y no publica por sí mismo",async()=>{
  const e=env(), p="/api/jobs/job-one/dossier";
  e.DB.jobs.get("job-one").status="approved";
  let fetchCount=0;
  const previous=globalThis.fetch;
  globalThis.fetch=async (...args)=>{fetchCount++;return new Response(null,{status:204})};
  try{
    assert.equal((await api(e,"/api/jobs/job-one/dispatch","POST",{})).status,409);
    assert.equal(fetchCount,0);
    // Mismo expediente acreditado y validado, sin saltarse review para autorizar publicación.
    e.DB.dossiers.set("job-one",{dossier_json:JSON.stringify(approved()),editor_attested:1,editor_name:"Revisor",attested_at:"now"});
    assert.equal((await api(e,"/api/jobs/job-one/dispatch","POST",{})).status,200);
    assert.equal(fetchCount,1);
    assert.equal(e.DB.jobs.get("job-one").status,"queued");
  } finally {globalThis.fetch=previous;}
});
