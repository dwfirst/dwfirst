"""ingest.py - read files from 09_inbox, chunk, index into Chroma.

Usage:
  python ingest.py            - index all .md/.txt from 09_inbox
  python ingest.py --move     - index + move originals to deep archive
  python ingest.py --path DIR - custom source dir (default X:/09_inbox)
  python ingest.py --dry      - dry run, no writes
"""
import os
import sys
import time
import hashlib
import argparse
import json

X = "X:" + os.sep
sys.path.insert(0, os.path.join(X, "05_chroma"))
sys.path.insert(0, os.path.join(X, "04_memory_long"))

INBOX = os.path.join(X, "09_inbox")
DEEP_ARCHIVE = os.path.join(X, "92_data", "archive")
HASHES_FILE = os.path.join(X, "05_chroma", "ingested_hashes.json")

CHUNK_CHARS = 1500
OVERLAP_CHARS = 300


def _file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()[:16]


def _load_hashes():
    if not os.path.exists(HASHES_FILE):
        return {}
    try:
        with open(HASHES_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_hashes(hashes):
    with open(HASHES_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)




def _extract_project(source_path):
    """If source is under 10_projects/<cat>/<proj>/, return 'cat/proj'. Else None."""
    try:
        norm = source_path.replace("\\", "/")
        marker = "10_projects/"
        idx = norm.find(marker)
        if idx < 0:
            return None
        rest = norm[idx + len(marker):]
        parts = rest.split("/")
        if len(parts) >= 2:
            return parts[0] + "/" + parts[1]
    except Exception:
        pass
    return None

def _read_text(path):
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        return f.read()


def _chunk_text(text, chunk_chars=CHUNK_CHARS, overlap_chars=OVERLAP_CHARS):
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = end - overlap_chars
    return chunks


def _find_files(source_dir, exts=(".md", ".txt")):
    out = []
    for root, dirs, files in os.walk(source_dir):
        dirs.sort()
        for f in sorted(files):
            if f.lower().endswith(exts):
                out.append(os.path.join(root, f))
    return out


def _ensure_dir(p):
    if not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)


def run(source_dir=INBOX, move=False, dry=False):
    import chroma_store as chroma

    _ensure_dir(DEEP_ARCHIVE)
    hashes = _load_hashes()
    files = _find_files(source_dir)

    if not files:
        print("[ingest] no .md/.txt files in", source_dir)
        return

    print("[ingest] found", len(files), "files")

    total_chunks = 0
    skipped = 0
    t0 = time.time()

    for fp in files:
        fname = os.path.basename(fp)
        fhash = _file_hash(fp)

        if fhash in hashes:
            print("  [skip]", fname, "(already indexed)")
            skipped += 1
            continue

        text = _read_text(fp)
        chunks = _chunk_text(text)
        if not chunks:
            print("  [empty]", fname)
            continue

        items = []
        for i, ch in enumerate(chunks):
            doc_id = fhash + "_" + str(i)
            items.append({
                "id": doc_id,
                "text": ch,
                "metadata": {
                    "origin": "user",
                    "confidence": "high",
                    "source_type": "file",
                    "source": str(fname),
                    "source_path": str(fp),
                    "project": str(_extract_project(fp) or ""),
                    "chunk_index": str(i),
                    "total_chunks": str(len(chunks)),
                    "file_hash": str(fhash),
                    "date": time.strftime("%Y-%m-%d"),
                },
            })

        if dry:
            print("  [dry]", fname, "->", len(chunks), "chunks")
            continue

        added = chroma.add_batch(items)
        total_chunks += added
        hashes[fhash] = {
            "file": fname,
            "chunks": added,
            "indexed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        print("  [ok]", fname, "->", added, "chunks")

        if move:
            dst = os.path.join(DEEP_ARCHIVE, fname)
            base, ext = os.path.splitext(fname)
            k = 1
            while os.path.exists(dst):
                dst = os.path.join(DEEP_ARCHIVE, base + "_" + str(k) + ext)
                k += 1
            os.rename(fp, dst)
            print("      moved to", dst)

    if not dry:
        _save_hashes(hashes)

    elapsed = round(time.time() - t0, 1)
    print("=== SUMMARY ===")
    print("files processed:", len(files))
    print("chunks added:", total_chunks)
    print("skipped:", skipped)
    print("elapsed:", elapsed, "sec")
    print("chroma count:", chroma.count())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=INBOX)
    ap.add_argument("--move", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    run(source_dir=args.path, move=args.move, dry=args.dry)
