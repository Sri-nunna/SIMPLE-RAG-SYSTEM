from pathlib import Path
import json
import re


def save_uploaded_files(uploaded_files, dest_dir="data/uploads"):
    """Save an iterable of Streamlit UploadedFile objects to disk.

    Files are saved under `dest_dir`. Returns a list of saved absolute paths.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    for uf in uploaded_files:
        out_path = dest / uf.name
        with open(out_path, "wb") as f:
            f.write(uf.getbuffer())
        saved.append(str(out_path.resolve()))
    return saved


def _sentences_of(text):
    parts = re.split(r'(?<=[\.\!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def _tokenize(text):
    # lowercase tokens, drop short tokens
    toks = re.findall(r"[a-z0-9']+", text.lower())
    return [t for t in toks if len(t) > 1]


def build_index(uploads_dir="data/uploads", index_path="data/index.json"):
    """Scan text files under `uploads_dir`, split into sentences and build a simple index.

    The index is a JSON list of objects: {file, sentence, tokens}.
    Returns the path to the index file.
    """
    uploads = Path(uploads_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    index = []
    for f in uploads.iterdir():
        if not f.is_file():
            continue
        try:
            txt = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for sent in _sentences_of(txt):
            # basic header/title filter: skip short question-like or title-like lines
            words = sent.split()
            # skip obvious questions (likely headings) and very short lines
            if sent.endswith('?') or len(words) < 4:
                continue
            # skip lines that are mostly Title Case (likely headings)
            titlecase_count = sum(1 for w in words if w[:1].isupper())
            if len(words) > 0 and (titlecase_count / len(words)) > 0.6 and len(words) < 10:
                continue

            index.append({
                "file": f.name,
                "sentence": sent,
                "tokens": _tokenize(sent)
            })

    idxp = Path(index_path)
    idxp.parent.mkdir(parents=True, exist_ok=True)
    with open(idxp, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=2)

    return str(idxp.resolve())