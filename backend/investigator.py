from pathlib import Path
import re


def analyze_evidence(paths):
    """Basic stub analysis: returns a minimal summary for uploaded evidence paths.

    Replace with real analysis logic that uses RAG, embeddings, or other tooling.
    """
    p = [str(x) for x in (paths or [])]
    return {
        "file_count": len(p),
        "files": p,
        "summary": f"Found {len(p)} evidence file(s)."
    }


def answer_query(paths, query):
    """Generate a simple answer for the provided `query` using the files in `paths`.

    This is a lightweight heuristic-based stub. Replace with real NLP/RAG logic later.
    """
    """
    Answer queries by searching a pre-built index (JSON) if `paths` is None or points to an index file.
    Otherwise, `paths` may be a list of file paths (legacy) and we'll read those.
    """
    import json
    from collections import Counter

    q = (query or "").strip()
    if not q:
        return {"answer": "No query provided.", "evidence_files": []}

    # load index
    index = []
    # If paths is a single string and looks like a file, try load
    if isinstance(paths, str) and paths.endswith('.json') and Path(paths).exists():
        try:
            index = json.loads(Path(paths).read_text(encoding='utf-8'))
        except Exception:
            index = []
    else:
        # try default index location
        default_idx = Path('data/index.json')
        if default_idx.exists():
            try:
                index = json.loads(default_idx.read_text(encoding='utf-8'))
            except Exception:
                index = []

    # fallback: if still no index, try reading files passed in `paths` (legacy behavior)
    if not index and paths:
        files = [Path(x) for x in (paths or [])]
        for f in files:
            try:
                txt = f.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            # split into sentences
            parts = re.split(r'(?<=[\.\!?])\s+', txt)
            for p in parts:
                s = p.strip()
                if s:
                    toks = re.findall(r"[a-z0-9']+", s.lower())
                    index.append({"file": f.name, "sentence": s, "tokens": [t for t in toks if len(t) > 1]})

    if not index:
        return {"answer": "No indexed evidence available. Please ingest files first.", "evidence_files": []}

    # Prefer TF-IDF retrieval if sklearn is available
    sentences = [it.get('sentence', '') for it in index]
    if not sentences or all(s == '' for s in sentences):
        return {"answer": "No valid sentences found in index.", "evidence_files": []}

    top = []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import linear_kernel

        vec = TfidfVectorizer(stop_words='english')
        mat = vec.fit_transform(sentences)
        q_vec = vec.transform([q])
        sims = linear_kernel(q_vec, mat).flatten()
        ranked_idx = sims.argsort()[::-1]
        # keep top 10 with positive score
        top = [index[i] for i in ranked_idx if sims[i] > 0][:10]
        # if none scored >0, still take top 5 closest
        if not top:
            top = [index[i] for i in ranked_idx][:5]
    except Exception as e:
        # fallback to token-overlap
        q_tokens = [t for t in re.findall(r"[a-z0-9']+", q.lower()) if len(t) > 1]
        if not q_tokens:
            # if no tokens, just return first few sentences
            top = index[:5]
        else:
            scores = []
            for item in index:
                tokset = set(item.get('tokens', []))
                score = sum(1 for t in q_tokens if t in tokset)
                if score > 0:
                    scores.append((score, item))
            scores.sort(key=lambda x: x[0], reverse=True)
            top = [it for _, it in scores[:10]]

    if not top:
        # if still no results, return the first few sentences as fallback
        top = index[:5]

    # helper to extract names
    name_re = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")

    # Build answers based on intent-like keywords
    lowq = q.lower()
    if any(k in lowq for k in ["suspect", "prime suspect"]):
        candidates = []
        # require suspect-like markers in the same sentence to consider name extraction
        suspect_markers = ["suspect", "identified", "named", "arrested", "charged", "accused", "detained"]
        for it in top:
            sent_low = it['sentence'].lower()
            if any(marker in sent_low for marker in suspect_markers):
                for m in name_re.findall(it['sentence']):
                    # accept only multi-word names (regex already enforces) and filter short tokens
                    if len(m.split()) >= 2:
                        candidates.append(m)

        candidates = list(dict.fromkeys(candidates))
        if candidates:
            answer = f"Possible suspect(s) mentioned in the evidence: {', '.join(candidates)}."
        else:
            # if no names found near suspect markers, provide the most relevant sentences as supporting evidence
            sents = [it['sentence'] for it in top[:5]]
            answer = "No clear suspect name found near suspect-related text. Relevant evidence:\n\n" + "\n\n".join(sents)

    elif any(k in lowq for k in ["2 am", "2:00", "02:00", "2am"]):
        # prefer sentences that explicitly mention time
        time_matches = [it['sentence'] for it in top if any(t in it['sentence'].lower() for t in ['2:00','2 am','02:00','2am','1:40','1:30','2:20','02:20'])]
        if time_matches:
            # synthesize a short answer from matching sentences
            answer = "Events around 2 AM from the evidence:\n\n" + "\n\n".join(time_matches[:5])
        else:
            # if no explicit time mentions, synthesize from top-ranked sentences
            sents = [it['sentence'] for it in top[:5]]
            answer = "No explicit 2 AM mentions found. Closest evidence snippets:\n\n" + "\n\n".join(sents)

    else:
        # generic: synthesize a short answer from top-ranked sentences
        if top:
            sents = [it['sentence'] for it in top[:5]]
            answer = "Based on the studied evidence, relevant information:\n\n" + "\n\n".join(sents)
        else:
            answer = "No relevant evidence snippets found for that query."

    files_seen = list({it['file'] for it in index})
    return {"answer": answer, "evidence_files": files_seen}