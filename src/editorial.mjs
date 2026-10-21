// Contrato editorial: estructura y puertas verificables, NO prueba de verdad factual.
const validTypes = new Set(["primaria", "secundaria"]);
const validEvidence = new Set(["pendiente", "verificada", "rechazada"]);
const validAssetTypes = new Set(["imagen", "video", "musica", "voz", "grafico"]);
const validRights = new Set(["pendiente", "verificado", "rechazado"]);

const string = (value, title, min, max) => {
  if (typeof value !== "string" || value.trim().length < min || value.trim().length > max)
    throw new Error(title + " debe tener entre " + min + " y " + max + " caracteres");
  return value.trim();
};
const list = (value, title, min, max) => {
  if (!Array.isArray(value) || value.length < min || value.length > max)
    throw new Error(title + ": se requieren " + min + "-" + max + " registros");
  return value;
};
export function sourceUrl(value) {
  if (typeof value !== "string" || value.length > 1000) throw new Error("URL de fuente inválida");
  let u;
  try { u = new URL(value); } catch { throw new Error("URL de fuente inválida"); }
  if (u.protocol !== "https:" || !u.hostname || u.username || u.password ||
      /^(localhost|127\\.|10\\.|192\\.168\\.|169\\.254\\.|0\\.)/i.test(u.hostname) ||
      u.hostname.endsWith(".local") || u.hostname.endsWith(".invalid"))
    throw new Error("La fuente requiere HTTPS público, sin credenciales");
  return u.href;
}
export function validateDossier(dossier, manifest) {
  if (!dossier || typeof dossier !== "object" || Array.isArray(dossier))
    throw new Error("El expediente debe ser un objeto JSON");
  const title = string(dossier.title, "Título de investigación", 8, 150);
  string(dossier.thesis, "Tesis editorial", 25, 550);
  if (dossier.publication_authorized !== false)
    throw new Error("Un expediente de investigación nunca autoriza publicación");
  const sources = list(dossier.sources, "Fuentes", 2, 30);
  const claims = list(dossier.claims, "Afirmaciones", 1, 50);
  const assets = list(dossier.assets, "Recursos audiovisuales", 1, 40);
  const sourceIds = new Set(), sourceUrls = new Set(), claimIds = new Set();
  for (const s of sources) {
    if (!s || typeof s !== "object") throw new Error("Fuente inválida");
    const sid = string(s.id, "ID de fuente", 3, 4);
    if (!/^S\\d{2,3}$/.test(sid) || sourceIds.has(sid)) throw new Error("ID de fuente duplicado o incorrecto");
    sourceIds.add(sid);
    const url = sourceUrl(s.url);
    if (sourceUrls.has(url)) throw new Error("Fuente URL duplicada");
    sourceUrls.add(url);
    string(s.publisher, "Entidad publicadora", 3, 130);
    const date = string(s.accessed_on, "Fecha de acceso", 10, 10);
    if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(date) ||
        Number.isNaN(Date.parse(date)) || new Date(date).toISOString().slice(0,10) !== date)
      throw new Error("Fecha de consulta inválida");
    if (!validTypes.has(s.type)) throw new Error("Tipo de fuente inválido");
  }
  if (manifest) {
    for (const url of manifest.sources) {
      if (!sourceUrls.has(sourceUrl(typeof url === "string" ? url : url.url)))
        throw new Error("Una fuente del guion no está documentada en el expediente");
    }
  }
  let verifiedClaims = 0;
  for (const c of claims) {
    if (!c || typeof c !== "object") throw new Error("Afirmación inválida");
    const cid = string(c.id, "ID de afirmación", 3, 4);
    if (!/^C\\d{2,3}$/.test(cid) || claimIds.has(cid)) throw new Error("ID de afirmación duplicado o inválido");
    claimIds.add(cid);
    string(c.text, "Texto de afirmación", 20, 900);
    const evidence = list(c.evidence, "Evidencia por afirmación", 1, 5);
    const seen = new Set();
    for (const e of evidence) {
      if (!e || !sourceIds.has(e.source_id) || seen.has(e.source_id))
        throw new Error("Evidencia sin fuente o repetida");
      seen.add(e.source_id);
      string(e.locator, "Sección o página de la fuente", 4, 220);
      if (!validEvidence.has(e.status)) throw new Error("Estado de evidencia inválido");
    }
    if (c.reviewed_by != null && c.reviewed_by !== "") string(c.reviewed_by, "Revisor de afirmación", 3, 100);
    if (evidence.every(e => e.status === "verificada") &&
        typeof c.reviewed_by === "string" && c.reviewed_by.trim().length >= 3) verifiedClaims++;
  }
  let verifiedAssets = 0, voiceDeclared = false;
  for (const a of assets) {
    if (!a || !validAssetTypes.has(a.kind)) throw new Error("Tipo de recurso inválido");
    string(a.description, "Descripción del recurso", 5, 250);
    if (!validRights.has(a.rights_status)) throw new Error("Estado de licencia inválido");
    if (a.kind === "voz") voiceDeclared = true;
    if (a.rights_status === "verificado") verifiedAssets++;
  }
  if (!voiceDeclared) throw new Error("Debe declararse al menos el recurso de voz y su licencia");
  return {
    title, source_count: sources.length, claim_count: claims.length,
    verified_claims: verifiedClaims, pending_claims: claims.length - verifiedClaims,
    asset_count: assets.length, pending_assets: assets.length - verifiedAssets,
    structurally_complete: claims.length === verifiedClaims && assets.length === verifiedAssets,
    publication_authorized: false
  };
}
