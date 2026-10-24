"""Enlace reproducible del guion a las citas activas; no acredita veracidad."""
import hashlib
import json


def evidence_link_sha256(research):
    core={'wikidata_id':research.get('selected_wikidata_id'),
          'evidence':[{k:e.get(k) for k in ('id','url','document_sha256','page','excerpt','source_class')}
                      for e in research.get('evidence_manifest',[])],
          'claims':[{k:c.get(k) for k in ('statement','evidence_ids')}
                    for c in research.get('candidate_claims',[])]}
    return hashlib.sha256(json.dumps(core,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
