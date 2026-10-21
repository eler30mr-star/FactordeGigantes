import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/worker.js";
import {validateResearchTopic,researchTopicKey,launchResearch,listResearchRequests,matchResearchRuns} from "../src/research-control.mjs";

const TOKEN="private-admin-token-for-tests-0001";
const ENV={GITHUB_REPO:"eler30mr-star/FactordeGigantes",GITHUB_DISPATCH_TOKEN:"private-github-token-for-tests-0001",ADMIN_TOKEN:TOKEN};
class ResearchDB {
  constructor(){this.requests=[];}
  prepare(sql){
    const db=this;
    return {
      args:[],
      bind(...values){this.args=values;return this},
      async first(){
        if(sql.includes("COUNT(*)"))return {total:db.requests.filter(x=>x.day_utc===this.args[0]).length};
        throw Error("Unexpected SQL first: "+sql);
      },
      async all(){
        if(sql.includes("FROM research_requests"))
          return {results:[...db.requests].reverse().slice(0,20).map(x=>({
            id:x.id,topic:x.topic,state:x.state,created_at:x.day_utc+" 12:00:00",updated_at:x.day_utc+" 12:00:00"
          }))};
        throw Error("Unexpected SQL all: "+sql);
      },
      async run(){
        if(sql.startsWith("INSERT OR IGNORE")) {
          const [id,topic,topic_key,day_utc]=this.args;
          if(db.requests.some(x=>x.topic_key===topic_key && x.day_utc===day_utc))
            return {meta:{changes:0}};
          db.requests.push({id,topic,topic_key,day_utc,state:"reserved"});
          return {meta:{changes:1}};
        }
        if(sql.startsWith("UPDATE research_requests")){
          const id=this.args[0], record=db.requests.find(x=>x.id===id);
          if(!record)return {meta:{changes:0}};
          const next=/state='(\w+)'/.exec(sql)?.[1];
          if(!next)throw Error("Unsupported update");
          record.state=next;return {meta:{changes:1}};
        }
        throw Error("Unexpected SQL run: "+sql);
      }
    };
  }
}
const now=new Date("2026-10-20T19:50:00Z");
const env=()=>({...ENV,DB:new ResearchDB()});

test("los temas aceptan español pero rechazan saltos y marcas",()=>{
  assert.equal(validateResearchTopic("  ¿Cómo surgió BlackBerry?  "),"¿Cómo surgió BlackBerry?");
  assert.equal(researchTopicKey("BlackBERRY"),"blackberry");
  for(const x of ["", "abc", "a".repeat(111), "BlackBerry\n<script>",
       "http://x", "BlackBerry\\Users"]) {
    if(x==="http://x")continue; // Una URL como tema es innecesaria pero no una ejecución de comandos.
    assert.throws(()=>validateResearchTopic(x));
  }
});

test("token configurado, confirmación, 204 y main; mismo tema se deduplica",async()=>{
  const e=env();
  let calls=0;
  const gh=async(url,options)=>{
    calls++;
    assert.match(url,/\/actions\/workflows\/research-ai-cpu.yml\/dispatches$/);
    assert.equal(options.method,"POST");
    assert.equal(JSON.parse(options.body).ref,"main");
    assert.equal(JSON.parse(options.body).inputs.topic,"La historia de BlackBerry");
    assert.match(JSON.parse(options.body).inputs.request_id,/^[0-9a-f-]{36}$/);
    assert.equal(options.headers.Authorization,"Bearer "+ENV.GITHUB_DISPATCH_TOKEN);
    return {status:204};
  };
  const before=await launchResearch(e,{topic:"BlackBerry",confirmed:false},gh,now);
  assert.equal(before.status,400);
  assert.equal(e.DB.requests.length,0);
  const yes=await launchResearch(e,{topic:"La historia de BlackBerry",confirmed:true},gh,now);
  assert.equal(yes.status,202);
  assert.equal(yes.request.state,"sent");
  assert.equal((await listResearchRequests(e)).requests[0].state,"sent");
  assert.equal((await launchResearch(e,{topic:"la HISTORIA de blackberry",confirmed:true},gh,now)).status,409);
  assert.equal(calls,1);
});

test("límite 4 solicitudes/día UTC; no despachar más trabajo pesado",async()=>{
  const e=env();let calls=0;
  for(let i=1;i<=4;i++){
    const result=await launchResearch(e,{topic:"Tema de negocios "+i,confirmed:true},
      async()=>{calls++;return {status:204}},now);
    assert.equal(result.status,202);
  }
  const fifth=await launchResearch(e,{topic:"Tema de negocios 5",confirmed:true},
    async()=>{calls++;return {status:204}},now);
  assert.equal(fifth.status,429);
  assert.equal(calls,4);
});

test("fallo de red no hace doble lanzamiento; rechazo explícito permanece trazado",async()=>{
  const e=env();
  const unknown=await launchResearch(e,{topic:"Historia de Apple",confirmed:true},
    async()=>{throw Error("network timeout")},now);
  assert.equal(unknown.status,502);
  assert.equal(e.DB.requests[0].state,"unknown");
  assert.equal((await launchResearch(e,{topic:"historia de apple",confirmed:true},
    async()=>{throw Error("should not call again")},now)).status,409);
  const reject=await launchResearch(e,{topic:"Historia de Intel",confirmed:true},
    async()=>({status:403}),now);
  assert.equal(reject.status,502);
  assert.equal(e.DB.requests[1].state,"rejected");
});

test("token, repositorio y petición sin credenciales son comprobados antes de reservar",async()=>{
  const e=env();
  delete e.GITHUB_DISPATCH_TOKEN;
  assert.equal((await launchResearch(e,{topic:"La historia de Samsung",confirmed:true},
    async()=>{throw Error("should not call")},now)).status,503);
  assert.equal(e.DB.requests.length,0);
  e.GITHUB_DISPATCH_TOKEN=ENV.GITHUB_DISPATCH_TOKEN;
  e.GITHUB_REPO="wrong/repo";
  assert.equal((await launchResearch(e,{topic:"La historia de Samsung",confirmed:true},
    async()=>{throw Error("should not call")},now)).status,503);
});

test("rutas privadas Worker GET y POST mantienen autenticación y 503 por falta de token Github",async()=>{
  const e=env();
  delete e.GITHUB_DISPATCH_TOKEN;
  const build=(method,credential,body)=>new Request("https://factor.test/api/research",{
    method,
    headers:{"Authorization":"Bearer "+credential,...(body?{"Content-Type":"application/json"}:{})},
    ...(body?{body:JSON.stringify(body)}:{})
  });
  const no=await worker.fetch(build("GET","invalid"),e);
  assert.equal(no.status,401);
  const yes=await worker.fetch(build("GET",TOKEN),e);
  assert.equal(yes.status,200);
  const post=await worker.fetch(build("POST",TOKEN,{topic:"Historia de Tesla",confirmed:true}),e);
  assert.equal(post.status,503);
  assert.equal(e.DB.requests.length,0);
});


test("estado real enlazado por request_id exacto y URL oficial de Actions",async()=>{
  const e=env();
  const launched=await launchResearch(e,{topic:"Historia de compañías innovadoras",confirmed:true},
    async()=>({status:204}),now);
  assert.equal(launched.status,202);
  const id=launched.request.id;
  let calls=0;
  const gh=async(url,options)=>{
    calls++;
    assert.match(url,/\/actions\/workflows\/research-ai-cpu.yml\/runs\?event=workflow_dispatch/);
    assert.match(options.headers.Authorization,/^Bearer /);
    return {ok:true,async json(){
      return {workflow_runs:[
        {id:77,event:"workflow_dispatch",head_branch:"main",display_title:"FDG Investigación · "+id,
         status:"completed",conclusion:"success",html_url:"https://github.com/eler30mr-star/FactordeGigantes/actions/runs/77"},
        {id:78,event:"workflow_dispatch",head_branch:"main",display_title:"FDG Investigación · other",
         status:"completed",conclusion:"failure",html_url:"https://github.com/eler30mr-star/FactordeGigantes/actions/runs/78"}
      ]};
    }};
  };
  const res=await listResearchRequests(e,{includeRuns:true,githubFetch:gh});
  assert.equal(calls,1);
  assert.equal(res.run_lookup,"checked");
  assert.equal(res.requests[0].run.id,77);
  assert.equal(res.requests[0].run.status,"completed");
  assert.equal(res.requests[0].run.conclusion,"success");
  assert.equal(res.requests[0].run.artifacts_url,"https://github.com/eler30mr-star/FactordeGigantes/actions/runs/77/artifacts");
  const cache=await listResearchRequests(e);
  assert.equal(cache.run_lookup,"not_requested");
  assert.equal(cache.requests[0].run,null);
});

test("no empareja ramas equivocadas, URL ajena ni ejecuciones manuales",()=>{
  const id="a1ea2f60-7464-4bea-8a6e-fad207ca0159";
  const rows=[{id}];
  const expected="FDG Investigación · "+id;
  const fake=[
    {id:2,event:"workflow_dispatch",head_branch:"other",display_title:expected,status:"completed",conclusion:"success",
     html_url:"https://github.com/eler30mr-star/FactordeGigantes/actions/runs/2"},
    {id:3,event:"workflow_dispatch",head_branch:"main",display_title:expected,status:"completed",conclusion:"success",
     html_url:"https://example.com/actions/runs/3"},
    {id:4,event:"push",head_branch:"main",display_title:expected,status:"completed",conclusion:"success",
     html_url:"https://github.com/eler30mr-star/FactordeGigantes/actions/runs/4"},
    {id:5,event:"workflow_dispatch",head_branch:"main",display_title:expected,status:"completed",conclusion:"failure",
     html_url:"https://github.com/eler30mr-star/FactordeGigantes/actions/runs/5"}
  ];
  const m=matchResearchRuns(rows,{workflow_runs:fake});
  assert.equal(m.size,1);
  assert.equal(m.get(id).id,5);
  assert.equal(m.get(id).conclusion,"failure");
});

test("fallo de lectura de GitHub nunca afirma que una ejecución finalizó",async()=>{
  const e=env();
  await launchResearch(e,{topic:"Empresas de telefonía histórica",confirmed:true},async()=>({status:204}),now);
  const unavailable=await listResearchRequests(e,{includeRuns:true,githubFetch:async()=>{throw Error("timeout")}});
  assert.equal(unavailable.run_lookup,"unavailable");
  assert.equal(unavailable.requests[0].state,"sent");
  assert.equal(unavailable.requests[0].run,null);
  const denied=await listResearchRequests(e,{includeRuns:true,githubFetch:async()=>({ok:false,status:403})});
  assert.equal(denied.run_lookup,"unavailable");
  assert.equal(denied.requests[0].run,null);
});
