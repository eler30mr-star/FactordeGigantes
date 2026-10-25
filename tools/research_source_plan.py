"""Búsquedas y ventanas textuales dirigidas a vacíos factuales, sin inferencia.

Los filtros y coincidencias son recuperación de candidatos, no corroboración.
No crean URLs, citas, hechos, licencias ni autorizaciones.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlsplit


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))


def prioritized_targets(targets):
    return sorted(targets, key=lambda t: (
        "no_regulatory_primary_document" not in t["gaps"],
        "no_original_primary_document" not in t["gaps"], t["claim_index"]))


def search_plan(title, targets, regulatory_domains, editorial_questions=None):
    excluded = ["wikipedia.org", "wikimedia.org", "wikidata.org"]
    if not targets:
        if editorial_questions:
            return [{'intent': 'find_primary_documents', 'query': f'"{title}" {editorial_questions[0]} original documents', 'exclude_domains': excluded},
                    {'intent': 'find_independent_context', 'query': f'"{title}" {editorial_questions[min(1, len(editorial_questions)-1)]} independent reporting', 'exclude_domains': excluded}]
        return [{"intent": "find_primary_documents", "query": f'"{title}" regulator court complaint financial statements',
                 "exclude_domains": excluded},
                {"intent": "find_independent_context", "query": f'"{title}" history annual report investigation original documents',
                 "exclude_domains": excluded}]
    ordered = prioritized_targets(targets)
    target = ordered[0]
    query = f'"{title}" ' + target["statement"][:220]
    regulatory = "no_regulatory_primary_document" in target["gaps"]
    official_query = query + " original annual report"
    if regulatory:
        statement=normalized(target['statement'])
        legal_terms=[term for pattern,term in (
            (r'fraud', 'fraud'), (r'imput|acus|indict|carg', 'indictment'),
            (r'conden|sentenc|convict', 'conviction sentencing'),
            (r'acuerd|settlement|restitu', 'settlement restitution'),
            (r'demand|complaint', 'complaint')) if re.search(pattern,statement)]
        years=list(dict.fromkeys(re.findall(r'\b(?:19|20)\d{2}\b',statement)))
        # La frase española completa devolvía BOE/DOJ ajenos al tema. Buscar
        # la entidad canónica y conceptos legales, sin inventar hechos ni URLs.
        official_query=' '.join([f'"{title}"',*legal_terms,*years,'court official'])
    primary = {"intent": "find_regulatory_original" if regulatory else "find_primary_original",
               "target_claim_index": target["claim_index"], "query": official_query,
               "exclude_domains": excluded}
    if regulatory:
        primary["include_domains"] = sorted(regulatory_domains)[:20]
    # La segunda consulta busca un emisor diferente del que ya sustenta el
    # hecho prioritario; no descartar a sus reguladores de la primera consulta.
    contrast_target = next((row for row in ordered if row['claim_index'] != target['claim_index']
        and 'no_independent_domain' in row['gaps']), target)
    cited = sorted({urlsplit(u).hostname for u in contrast_target["cited_urls"]})
    contrast_query = f'"{title}" ' + contrast_target['statement'][:220]
    contrast = {"intent": "find_independent_corroboration", "target_claim_index": contrast_target["claim_index"],
                "query": contrast_query, "exclude_domains": list(dict.fromkeys(excluded + cited))[:20]}
    return [primary, contrast]


def select_passages(analysis, title, targets, limit=3, editorial_questions=None):
    """Elegir bloques y ventanas literales; el localizador sigue siendo original."""
    blocks = [" ".join(b.split()) for b in analysis["blocks"]]
    company_words = set(re.findall(r"\w{3,}", normalized(title))) - {
        "empresa", "company", "corporation", "group", "inc", "limited", "grupo"}
    def mentions(text):
        value = normalized(text)
        return normalized(title) in value or bool(company_words & set(re.findall(r"\w+", value)))
    def features(text):
        return set(re.findall(r"\d+(?:[.,]\d+)*|[^\W\d_]{4,}", normalized(text))) - company_words
    wanted = [features(t["statement"]) for t in prioritized_targets(targets)]
    if not wanted and editorial_questions: wanted = [features(question) for question in editorial_questions]
    named = {i for i, text in enumerate(blocks) if mentions(text)}
    candidates = []
    for i, text in enumerate(blocks):
        if len(text) < 90:
            continue
        if len(re.findall(r'https?://',text))>=2:
            continue  # Bibliografía: sirve para descubrir enlaces, no como hecho.
        context = next((j for j in range(max(0, i-2), i+1) if j in named and
                        analysis["page_map"][j] == analysis["page_map"][i]), None)
        if i not in named and context is None:
            continue
        scores = []
        for target in wanted:
            overlap = features(text) & target
            scores.append(sum(8 if token[0].isdigit() else 1 for token in overlap))
        if i not in named and (not scores or max(scores) < 2):
            continue
        candidates.append({"index": i, "text": text, "scores": scores,
                           "context": None if i in named else blocks[context]})
    chosen = []
    # Cubrir objetivos distintos antes de ocupar tres espacios con la misma
    # introducción. Los empates conservan el orden documental.
    for n in range(len(wanted)):
        available = [c for c in candidates if c not in chosen and c["scores"][n] > 0]
        if available:
            chosen.append(max(available, key=lambda c: c["scores"][n]))
        if len(chosen) >= limit:
            break
    for c in sorted(candidates, key=lambda c: -max(c["scores"], default=0)):
        if len(chosen) >= limit:
            break
        if c not in chosen:
            chosen.append(c)
    results = []
    all_features = set().union(*wanted) if wanted else set()
    for c in chosen:
        text = c["text"]
        matches = [m for m in re.finditer(r"\w+(?:[.,]\d+)*", text)
                   if normalized(m.group()) in all_features]
        entity_matches = [m for m in re.finditer(r"\w+", text) if normalized(m.group()) in company_words]
        starts = [0] + [max(0, m.start()-60) for m in matches + entity_matches]
        # No cortar palabras en los bordes de la ventana.
        windows = []
        for start in starts:
            while start > 0 and start < len(text) and not text[start-1].isspace():
                start += 1
            end = min(len(text), start+320)
            if end < len(text):
                while end > start and not text[end].isspace():
                    end -= 1
            excerpt = text[start:end].strip()
            if len(excerpt) >= 90:
                overlap = features(excerpt) & all_features
                score = sum(8 if token[0].isdigit() else 1 for token in overlap)
                windows.append((score, int(mentions(excerpt)), -start, excerpt))
        if not windows:
            continue
        excerpt = max(windows)[3]
        record = {"block_index": c["index"], "page": analysis["page_map"][c["index"]],
                  "excerpt": excerpt, "selection_method": "targeted_literal_window_v1"}
        if c["context"]:
            record["entity_context_excerpt"] = c["context"][:180]
        elif not mentions(excerpt) and entity_matches:
            begin = max(0, entity_matches[0].start()-40)
            record["entity_context_excerpt"] = text[begin:begin+180]
        results.append(record)
    return results

