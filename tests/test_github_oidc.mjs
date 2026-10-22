import test from "node:test";
import assert from "node:assert/strict";
import {generateKeyPairSync,sign} from "node:crypto";
import {allowedMarketClaims,verifyMarketOIDC,MARKET_AUDIENCE} from "../src/github-oidc.mjs";

const TIME=1792600000;
function claims() {
 return {iss:"https://token.actions.githubusercontent.com",aud:MARKET_AUDIENCE,
   repository_id:"1426522491",repository:"eler30mr-star/FactordeGigantes",
   ref:"refs/heads/main",
   workflow_ref:"eler30mr-star/FactordeGigantes/.github/workflows/topic-discovery-smoke.yml@refs/heads/main",
   event_name:"schedule",runner_environment:"github-hosted",
   iat:TIME-60,nbf:TIME-60,exp:TIME+240};
}
test("permite solo workflow exacto en main con expiración próxima",()=>{
 assert.equal(allowedMarketClaims(claims(),TIME),true);
 for(const change of [
  x=>x.repository_id="111",x=>x.ref="refs/heads/dev",
  x=>x.workflow_ref="eler30mr-star/FactordeGigantes/.github/workflows/render.yml@refs/heads/main",
  x=>x.aud="untrusted",x=>x.event_name="pull_request",x=>x.event_name="push",x=>x.exp=TIME-100,
  x=>x.iat=TIME+1000,x=>x.runner_environment="self-hosted"
 ]){
  const copy=claims();change(copy);
  assert.equal(allowedMarketClaims(copy,TIME),false);
 }
});
function b64(o){return Buffer.from(JSON.stringify(o)).toString("base64url");}
test("verifica firma RSA real con llave publicada por JWKS de GitHub",async()=>{
 const {publicKey,privateKey}=generateKeyPairSync("rsa",{modulusLength:2048});
 const header=b64({alg:"RS256",typ:"JWT",kid:"factor-test-kid"});
 const payload=b64(claims());
 const data=header+"."+payload;
 const jwt=data+"."+sign("RSA-SHA256",Buffer.from(data),privateKey).toString("base64url");
 let calls=0;
 const fetcher=async u=>{
  calls++;assert.equal(u,"https://token.actions.githubusercontent.com/.well-known/jwks");
  return {ok:true,json:async()=>({keys:[{...publicKey.export({format:"jwk"}),
     kid:"factor-test-kid",use:"sig",alg:"RS256"}]})};
 };
 const request=token=>({headers:new Headers({Authorization:"Bearer "+token})});
 assert.equal(await verifyMarketOIDC(request(jwt),{fetcher,nowSeconds:TIME}),true);
 assert.equal(await verifyMarketOIDC(request(jwt.slice(0,-3)+"abc"),{fetcher,nowSeconds:TIME}),false);
 assert.equal(await verifyMarketOIDC(request(jwt.replace(/^eyJ/,"eyB")),{fetcher,nowSeconds:TIME}),false);
 assert.ok(calls>=2);
});
test("descarta credenciales sin firma o de token admin, sin consultar red",async()=>{
 const fetcher=()=>{throw Error("No debe consultar keys");};
 assert.equal(await verifyMarketOIDC({headers:new Headers({Authorization:"Bearer token-administrador"})},
   {fetcher,nowSeconds:TIME}),false);
});
