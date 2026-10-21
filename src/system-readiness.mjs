// Estado privado de producción. Nunca devuelve secretos ni aprueba material.
const REQUIRED = ["jobs","events","editorial_dossiers","research_requests"];
export async function systemReadiness(env) {
  const tableResult = await env.DB.prepare(
    "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('jobs','events','editorial_dossiers','research_requests')"
  ).all();
  const available = new Set((tableResult.results || []).map(row=>row.name));
  const tables = Object.fromEntries(REQUIRED.map(name=>[name,available.has(name)]));
  const githubRepositoryConfigured = env.GITHUB_REPO === "eler30mr-star/FactordeGigantes";
  const dispatchTokenPresent = typeof env.GITHUB_DISPATCH_TOKEN === "string" &&
    env.GITHUB_DISPATCH_TOKEN.length >= 24;
  return {
    product:"Factor de Gigantes",
    production_d1:tables,
    database_complete:REQUIRED.every(name=>tables[name]),
    github_repository_configured:githubRepositoryConfigured,
    github_dispatch_secret_present:dispatchTokenPresent,
    research_prerequisites_present:tables.research_requests && tables.jobs &&
       githubRepositoryConfigured && dispatchTokenPresent,
    render_prerequisites_present:tables.jobs && tables.events && tables.editorial_dossiers &&
       githubRepositoryConfigured,
    checks_do_not_certify_external_permissions:true,
    external_github_permissions_verified:false,
    copyright_or_fact_review_automatic:false,
    publication_authorized:false,
    note:"Comprobación local del Worker y D1. No ejecuta IA, no prueba permisos de GitHub ni autoriza publicar."
  };
}
