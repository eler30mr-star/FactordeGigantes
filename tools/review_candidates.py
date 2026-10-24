"""Elegir pasajes a comparar; la similitud sólo ordena, nunca verifica apoyo."""
from __future__ import annotations
import re
from urllib.parse import urlsplit
from tools.research_source_plan import normalized

METHOD='per_excerpt_support_v2'


def review_tasks(evidence, claims):
    company_words=set(re.findall(r'\w{3,}',normalized(evidence[0].get('company','')))) if evidence else set()
    def features(text):
        out=set(re.findall(r'\w{3,}',normalized(text)))
        for pattern,label in ((r'fund[oa]|found','founding'),(r'sanitari|health|salud','health'),
                (r'tecnolog|technolog','technology'),(r'fraud','fraud'),
                (r'inversion|investor','investor'),(r'conspir','conspiracy'),
                (r'imput|acusad|charged|indict','charged'),(r'electronic|wire','wire')):
            if re.search(pattern,normalized(text)):out.add(label)
        return out-company_words-{'empresa','company','sobre','para','with','that','from','fue','una','los','las'}
    by_id={e['id']:e for e in evidence}
    tasks=[]
    for n,claim in enumerate(claims,1):
        chosen=list(claim['evidence_ids'])
        hosts={urlsplit(by_id[x]['url']).hostname for x in chosen}
        hashes={by_id[x]['document_sha256'] for x in chosen}
        wanted=features(claim['statement'])
        def score(e):
            overlap=wanted & features(e['excerpt'])
            return sum(10 if x[0].isdigit() else 1 for x in overlap)
        ranked=sorted((e for e in evidence if e['id'] not in chosen),
                      key=lambda e:(-score(e),e['id']))
        # Primero otros dominios y documentos; incluir un segundo fragmento de
        # un mismo documento nunca satisface el contador de fuentes distintas.
        for item in ranked:
            if len(chosen)>=max(3,len(claim['evidence_ids'])):break
            host=urlsplit(item['url']).hostname
            if host in hosts or item['document_sha256'] in hashes:continue
            chosen.append(item['id']);hosts.add(host);hashes.add(item['document_sha256'])
        tasks.append({'claim_index':n,'inspect_evidence_ids':chosen})
    return tasks
