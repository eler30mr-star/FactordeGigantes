// Control de lanzamientos de investigación: coste finito y nunca publicación.
// No se combina con render.yml; usa únicamente research-ai-cpu.yml.
const WORKFLOW = "research-ai-cpu.yml";
const DAILY_LIMIT = 4;
export const workflowUrl = "https://github.com/eler30mr-star/FactordeGigantes/actions/workflows/" + WORKFLOW;

export function validateResearchTopic(input) {
  if (typeof input !== "string") throw new Error("Escribe un tema de investigación");
  const topic=input.normalize("NFKC").trim().replace(/ +/g," ");
  if (topic.length < 5 || topic.length > 110) throw new Error("Tema entre 5 y 110 caracteres");
  if (/[\x00-\x1F\x7F<>\\]/u.test(topic)) throw new Error("Tema contiene caracteres no permitidos");
  if (!/[\p{L}\p{N}]/u.test(topic)) throw new Error("El tema debe tener letras o números");
  return topic;
}

export function researchTopicKey(topic) {
  return topic.toLocaleLowerCase("es").normalize("NFKC");
}

export async function listResearchRequests(env) {
  const result=await env.DB.prepare(
    "SELECT id,topic,state,created_at,updated_at FROM research_requests ORDER BY created_at DESC LIMIT 20"
  ).all();
  return {requests:result.results,workflow_url:workflowUrl,daily_limit:DAILY_LIMIT,
          outcome_note:"Enviado solo significa aceptación de la solicitud; revisa Actions para el resultado."};
}

export async function launchResearch(env, payload, githubFetch=fetch, now=new Date()) {
  if (!payload || payload.confirmed !== true)
    return {ok:false,status:400,error:"Confirma expresamente que deseas utilizar minutos de GitHub Actions."};
  const topic=validateResearchTopic(payload.topic);
  const repo=env.GITHUB_REPO;
  if (repo !== "eler30mr-star/FactordeGigantes")
    return {ok:false,status:503,error:"Repositorio de investigación no configurado para Factor de Gigantes"};
  if (!env.GITHUB_DISPATCH_TOKEN || env.GITHUB_DISPATCH_TOKEN.length<24)
    return {ok:false,status:503,error:"Token GitHub Actions no configurado"};
  const day=now.toISOString().slice(0,10);
  const quota=await env.DB.prepare(
    "SELECT COUNT(*) AS total FROM research_requests WHERE day_utc=?"
  ).bind(day).first();
  if (Number(quota?.total||0)>=DAILY_LIMIT)
    return {ok:false,status:429,error:"Límite de cuatro investigaciones solicitadas por día UTC alcanzado"};
  const id=crypto.randomUUID();
  const inserted=await env.DB.prepare(
    "INSERT OR IGNORE INTO research_requests(id,topic,topic_key,day_utc,state) VALUES(?,?,?,?,'reserved')"
  ).bind(id,topic,researchTopicKey(topic),day).run();
  if (inserted.meta?.changes !== 1)
    return {ok:false,status:409,error:"Este tema ya fue solicitado hoy; revisa Actions antes de repetir"};
  const endpoint="https://api.github.com/repos/"+repo+"/actions/workflows/"+WORKFLOW+"/dispatches";
  let response;
  try {
    response=await githubFetch(endpoint,{method:"POST",headers:{
      "Authorization":"Bearer "+env.GITHUB_DISPATCH_TOKEN,
      "Accept":"application/vnd.github+json",
      "X-GitHub-Api-Version":"2022-11-28",
      "User-Agent":"FactorDeGigantes-Investigador",
      "Content-Type":"application/json"
    },body:JSON.stringify({ref:"main", inputs:{topic}})});
  } catch {
    await env.DB.prepare(
      "UPDATE research_requests SET state='unknown',updated_at=datetime('now') WHERE id=? AND state='reserved'"
    ).bind(id).run();
    return {ok:false,status:502,error:"Resultado de red incierto. Revisa Actions; bloqueado el reenvío del mismo tema por hoy."};
  }
  if (response.status !== 204) {
    await env.DB.prepare(
      "UPDATE research_requests SET state='rejected',updated_at=datetime('now') WHERE id=? AND state='reserved'"
    ).bind(id).run();
    return {ok:false,status:502,error:"GitHub rechazó la solicitud de investigación (HTTP "+response.status+"). Revisa el token Actions."};
  }
  await env.DB.prepare(
    "UPDATE research_requests SET state='sent',updated_at=datetime('now') WHERE id=? AND state='reserved'"
  ).bind(id).run();
  return {ok:true,status:202,request:{id,topic,state:"sent"},
          workflow_url:workflowUrl,
          notice:"GitHub aceptó la solicitud; la ejecución y los resultados deben comprobarse en Actions. No se publicará ningún video."};
}
