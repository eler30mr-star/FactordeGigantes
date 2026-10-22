// Confianza restringida: solo el workflow de radar del repo oficial, rama main.
// GitHub OIDC: JWT efímero firmado por GitHub, sin secreto compartido.
export const MARKET_AUDIENCE="factor-de-gigantes-market-v1";
const ISSUER="https://token.actions.githubusercontent.com";
const JWKS="https://token.actions.githubusercontent.com/.well-known/jwks";
const WORKFLOW="eler30mr-star/FactordeGigantes/.github/workflows/topic-discovery-smoke.yml@refs/heads/main";
const REPO_ID="1426522491";
const textEncoder=new TextEncoder();

function decode64(value) {
  if(typeof value!=="string" || !/^[A-Za-z0-9_-]+$/.test(value)) throw Error("JWT base64 inválido");
  const binary=atob(value.replace(/-/g,"+").replace(/_/g,"/"));
  return Uint8Array.from(binary,c=>c.charCodeAt(0));
}
const parsePart=value=>JSON.parse(new TextDecoder().decode(decode64(value)));
export function allowedMarketClaims(claims, nowSeconds=Math.floor(Date.now()/1000)) {
  if(!claims || typeof claims!=="object") return false;
  // No fiarse de 'sub' textual: GitHub introdujo formato de sujeto inmutable.
  if(claims.iss!==ISSUER || claims.aud!==MARKET_AUDIENCE ||
     claims.repository_id!==REPO_ID ||
     claims.repository!=="eler30mr-star/FactordeGigantes" ||
     claims.ref!=="refs/heads/main" ||
     claims.workflow_ref!==WORKFLOW ||
     !["schedule","workflow_dispatch","push"].includes(claims.event_name) ||
     claims.runner_environment!=="github-hosted") return false;
  const {exp,nbf,iat}=claims;
  if(!Number.isSafeInteger(exp) || !Number.isSafeInteger(iat) ||
    !Number.isSafeInteger(nbf) || iat>nowSeconds+60 ||
    nbf>nowSeconds+60 || exp<=nowSeconds-30 || exp-iat>1200 ||
    exp<iat || exp-nbf>1200) return false;
  return true;
}
export async function verifyMarketOIDC(request,{fetcher=fetch,nowSeconds=Math.floor(Date.now()/1000)}={}) {
  try {
    const auth=request.headers.get("Authorization")||"";
    if(!auth.startsWith("Bearer ") || auth.length>12000) return false;
    const parts=auth.slice(7).split(".");
    if(parts.length!==3) return false;
    const [h,p,s]=parts;
    const header=parsePart(h);
    if(header.alg!=="RS256" || typeof header.kid!=="string" ||
       header.kid.length>150 || header.kid.length<5 ||
       !/^[a-zA-Z0-9_\-.]+$/.test(header.kid) ||
       (header.typ && header.typ!=="JWT")) return false;
    const claims=parsePart(p);
    if(!allowedMarketClaims(claims,nowSeconds)) return false;
    const response=await fetcher(JWKS,{headers:{Accept:"application/json"}});
    if(!response.ok) return false;
    const document=await response.json();
    const jwk=document?.keys?.find(key=>key.kid===header.kid &&
       key.kty==="RSA" && key.alg==="RS256" && key.use==="sig");
    if(!jwk) return false;
    const key=await crypto.subtle.importKey("jwk",jwk,{name:"RSASSA-PKCS1-v1_5",hash:"SHA-256"},false,["verify"]);
    return await crypto.subtle.verify("RSASSA-PKCS1-v1_5",key,decode64(s),textEncoder.encode(h+"."+p));
  } catch {
    return false;
  }
}
