// Aceptación de lectura contra GitHub; no despacha workflows ni invoca IA.
import {readProductionProgress} from '../src/production-progress.mjs';
const env={GITHUB_REPO:'eler30mr-star/FactordeGigantes',GITHUB_DISPATCH_TOKEN:process.env.GH_TOKEN};
const listed=await readProductionProgress(env);
if(!listed.ok)throw Error(listed.error);
const run=listed.runs[0];
if(!run){console.log('PRODUCCION: sin ejecuciones registradas');process.exit(0);}
const result=await readProductionProgress(env,run.id);
if(!result.ok)throw Error(result.error);
console.log('PRODUCCION_OBSERVADA:',JSON.stringify({run_id:run.id,
 scenes_completed:result.narration.completed,scenes_total:result.narration.total,
 scene_failures:result.narration.failed,exports:result.results.map(r=>({narrated:r.contains_narration,bytes:r.size_bytes})),
 publication_authorized:false,ai_calls:0}));
