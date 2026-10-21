import assert from "node:assert/strict";
import test from "node:test";
import {readMarketRadar} from "../src/market-radar.mjs";
function db(queries, fail=false) {
  return {
    DB: {
      prepare(sql) {
        queries.push(sql);
        return {
          bind(limit) {
            return {
              async all() {
                if (fail) throw Error("D1_ERROR: no such table: market_runs");
                return {results:[{limit}]};
              }
            };
          }
        };
      }
    }
  };
}

test("radar administrativo solo consulta y nunca autoriza publicación",async()=>{
 const queries=[];
 const result=await readMarketRadar(db(queries),new URL("https://factor.example/api/market/radar?limit=9"));
 assert.equal(result.ok,true);
 assert.equal(result.market_study_complete,false);
 assert.equal(result.automatic_publication_allowed,false);
 assert.equal(result.youtube_data_verified,false);
 assert.equal(queries.length,3);
 assert.ok(queries.every(q=>q.startsWith("SELECT ") && q.includes("LIMIT ?")));
 assert.deepEqual(result.runs,[{limit:9}]);
});
test("valida límites antes de acceder a D1",async()=>{
 const q=[];for(const n of ["0","101","1;DROP TABLE jobs","-5","1.5"]){
  const result=await readMarketRadar(db(q),new URL("https://factor.example/api/market/radar?limit="+encodeURIComponent(n)));
  assert.equal(result.status,400);
 }
 assert.equal(q.length,0);
});
test("identifica migración pendiente sin filtrar excepción SQL",async()=>{
 const result=await readMarketRadar(db([],true),new URL("https://factor.example/api/market/radar"));
 assert.equal(result.status,503);
 assert.match(result.error,/0004/);
});
