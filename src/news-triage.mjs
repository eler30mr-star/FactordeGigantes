// Puntuación editorial EXPLORATORIA para priorizar lectura. NO predice audiencia.
// Sin LLM, sin estimación de demanda YouTube, sin decisiones de investigación/publicación.
const SIGNALS=[
  ["cambio_estrategico",25,/\b(transformation|transformacion|transformación|pivot|reestructura|reinvent|turnaround|giro estrategico|giro estratégico|cambia de rumbo|restructur)\b/i],
  ["disrupcion_innovacion",24,/\b(breakthrough|innovation|innovaci[oó]n|disrupt|patent|patente|invento|invent|nueva tecnolog[ií]a|new technology|discovery)\b/i],
  ["empresa_y_modelo",19,/\b(company|companies|corporation|empresa|corporaci[oó]n|fabricante|manufacturer|startup|start-up|industria|industrial|business|negocio)\b/i],
  ["decisiones_competencia",22,/\b(acquisition|adquisici[oó]n|merger|fusi[oó]n|competencia|monopoly|monopolio|market share|quiebra|bankrupt|collapse|fracaso|cierre|expansion|expansi[oó]n)\b/i],
  ["tecnologia_industrial",14,/\b(artificial intelligence|inteligencia artificial|semiconductor|chips|robotic|rob[oó]tica|aerospace|software|automotive|automotriz|battery|bater[ií]a|manufacturing|fabricaci[oó]n)\b/i]
];
const LOW_RELEVANCE=[
  ["consejo_compra",30,/\b(c[oó]mo comprar|how to buy|tips for|investment advice|consejos para invertir|mejores acciones|best stocks|stock picks)\b/i],
  ["cotizacion_especulativa",22,/\b(price target|share price|stock price|precio de la acci[oó]n|predicci[oó]n de precio|dividend|dividendo|crypto price)\b/i],
  ["contenido_promocional",15,/\b(sponsored|patrocinado|descuento|sale now|shopping guide|coupon|cup[oó]n)\b/i]
];
export function triageNewsLeads(leads,now=Date.now()) {
  if(!Array.isArray(leads))throw new TypeError("Lista de noticias inválida");
  return leads.map(item=>{
    const text=String(item.headline||"");
    const positives=SIGNALS.filter(([,weight,rx])=>weight>0 && rx.test(text));
    const negatives=LOW_RELEVANCE.filter(([,weight,rx])=>weight>0 && rx.test(text));
    const observed=Date.parse(item.published_at||"");
    const hours=Number.isFinite(observed)?Math.max(0,(now-observed)/3600000):Infinity;
    const freshness=hours<=24?12:hours<=48?7:hours<=72?3:0;
    const score=Math.max(0,Math.min(100,
      positives.reduce((n,x)=>n+x[1],0)-negatives.reduce((n,x)=>n+x[1],0)+freshness));
    return {
      id:item.id,headline:text,category:item.category,source_label:item.source_label,
      published_at:item.published_at,aggregator_url:item.aggregator_url,
      editorial_relevance_score:score,
      heuristic_reasons:positives.map(x=>x[0]).concat(negatives.map(x=>"penalizacion_"+x[0])),
      news_evidence_only:true,market_qualified:false,
      youtube_market_verified:false,approved_for_research:false,
      editorial_status:"news_requires_original_source_and_youtube_comparison"
    };
  }).sort((a,b)=>b.editorial_relevance_score-a.editorial_relevance_score ||
      String(b.published_at).localeCompare(String(a.published_at)) ||
      String(a.id).localeCompare(String(b.id)));
}
