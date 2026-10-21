import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/worker.js";
import {systemReadiness} from "../src/system-readiness.mjs";

const ADMIN="factor-readiness-admin-token-tests-00000";
const DISPATCH="factor-readiness-secret-not-to-disclose-00000";
const REPO="eler30mr-star/FactordeGigantes";
function env(names=["jobs","events","editorial_dossiers","research_requests"]) {
  const queries=[];
  const value={
    ADMIN_TOKEN:ADMIN,
    RENDERER_TOKEN:"factor-renderer-token-other-test-00000",
    GITHUB_DISPATCH_TOKEN:DISPATCH,
    GITHUB_REPO:REPO,
    DB:{
      prepare(sql) {
        queries.push(sql);
        assert.match(sql,/SELECT name FROM sqlite_master WHERE type='table'/);
        return {async all(){return {results:names.map(name=>({name}))}}};
      }
    }
  };
  return {value,queries};
}
test("tablas completas y secretos solo generan banderas, sin valores sensibles",async()=>{
  const {value,queries}=env();
  const status=await systemReadiness(value);
  assert.equal(status.database_complete,true);
  assert.equal(status.github_dispatch_secret_present,true);
  assert.equal(status.research_prerequisites_present,true);
  assert.equal(status.render_prerequisites_present,true);
  assert.equal(status.external_github_permissions_verified,false);
  assert.equal(status.publication_authorized,false);
  assert.equal(queries.length,1);
  assert.ok(!JSON.stringify(status).includes(DISPATCH));
  assert.ok(!JSON.stringify(status).includes(ADMIN));
});
test("faltan migraciones: no declara investigación lista",async()=>{
  const {value}=env(["jobs","events"]);
  const status=await systemReadiness(value);
  assert.equal(status.database_complete,false);
  assert.equal(status.research_prerequisites_present,false);
  assert.equal(status.render_prerequisites_present,false);
  assert.equal(status.production_d1.editorial_dossiers,false);
  assert.equal(status.production_d1.research_requests,false);
});
test("token GitHub ausente no se confunde con permiso válido",async()=>{
  const {value}=env();
  delete value.GITHUB_DISPATCH_TOKEN;
  const status=await systemReadiness(value);
  assert.equal(status.github_dispatch_secret_present,false);
  assert.equal(status.research_prerequisites_present,false);
  assert.equal(status.external_github_permissions_verified,false);
});
test("solo ADMIN_TOKEN obtiene diagnóstico y solo mediante GET",async()=>{
  const {value}=env();
  const build=(method,token)=>new Request("https://factor.example/api/system/status",{
    method,headers:{"Authorization":"Bearer "+token}
  });
  assert.equal((await worker.fetch(build("GET","invalid"),value)).status,401);
  assert.equal((await worker.fetch(build("GET",value.RENDERER_TOKEN),value)).status,401);
  assert.equal((await worker.fetch(build("POST",ADMIN),value)).status,405);
  const response=await worker.fetch(build("GET",ADMIN),value);
  assert.equal(response.status,200);
  const data=await response.json();
  assert.equal(data.database_complete,true);
  assert.equal(data.publication_authorized,false);
  assert.equal(response.headers.get("Cache-Control"),"no-store");
});
