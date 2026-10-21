import test from "node:test";
import assert from "node:assert/strict";
import {triageNewsLeads} from "../src/news-triage.mjs";
const now=Date.parse("2026-10-21T20:00:00Z");
const item=(id,headline,published_at="2026-10-21T18:00:00Z")=>({
 id,headline,source_label:"Medio de ejemplo",category:"tecnologia",
 published_at,aggregator_url:"https://news.google.com/rss/articles/fake"
});
test("prioriza cambios industriales frente a guías financieras y conserva razones",()=>{
 const result=triageNewsLeads([
  item("b","How to buy the best stocks: stock price and dividend"),
  item("a","Technology company announces artificial intelligence breakthrough after strategic transformation"),
 ],now);
 assert.equal(result[0].id,"a");
 assert.ok(result[0].editorial_relevance_score>result[1].editorial_relevance_score);
 assert.ok(result[0].heuristic_reasons.includes("disrupcion_innovacion"));
 assert.equal(result[0].market_qualified,false);
 assert.equal(result[0].youtube_market_verified,false);
 assert.equal(result[0].approved_for_research,false);
 assert.equal(result[0].news_evidence_only,true);
});
test("no inventa interés de mercado ni elige tema si no hay señales",()=>{
 const result=triageNewsLeads([item("c","Un titular sin evidencia adicional")],now);
 assert.equal(result.length,1);
 assert.equal(result[0].market_qualified,false);
 assert.equal(result[0].editorial_status,"news_requires_original_source_and_youtube_comparison");
 assert.ok(result[0].editorial_relevance_score<=12);
 assert.deepEqual(triageNewsLeads([],now),[]);
});
