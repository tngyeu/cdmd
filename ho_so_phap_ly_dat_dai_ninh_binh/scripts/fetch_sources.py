"""Download an explicit JSON job list; preserve originals and log every outcome."""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import gzip
import json
import os
from pathlib import Path
import sys
import urllib.request
from urllib.parse import quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")

def fetch(job):
    record = dict(job)
    record["checked_at"] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    target = (ROOT / job["path"]).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError("Download target must be inside the module")
    try:
        parts = urlsplit(job["url"])
        url = urlunsplit((parts.scheme,parts.netloc,quote(parts.path,safe="/%:@"),quote(parts.query,safe="=&%+/:@?"),parts.fragment))
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (public legal research)"})
        with urllib.request.urlopen(request, timeout=job.get("timeout", 18)) as response:
            raw = response.read(35_000_000)
            record["resolved_url"] = response.url
            record["content_type"] = response.headers.get("Content-Type", "")
        if raw.startswith(b"\x1f\x8b"):
            raw = gzip.decompress(raw)
        if target.suffix == ".pdf" and not raw.startswith(b"%PDF"):
            raise ValueError("Response is not a PDF")
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(raw).hexdigest()
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            target = target.with_name(target.stem + "_" + digest[:10] + target.suffix)
        target.write_bytes(raw)
        record.update(status="downloaded", path=target.relative_to(ROOT).as_posix(), bytes=len(raw), sha256=digest)
    except Exception as exc:
        record.update(status="unavailable", error=str(exc))
    return record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jobs", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    jobs = json.loads(args.jobs.read_text(encoding="utf-8-sig"))
    log = ROOT / "data/download_log.jsonl"
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, args.workers)) as pool:
        for index, record in enumerate(pool.map(fetch, jobs), 1):
            with log.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            if record['status']!='downloaded' or index%25==0 or index==len(jobs):
                print(json.dumps(dict(progress=f'{index}/{len(jobs)}',**{key:record.get(key) for key in ("path", "status", "bytes", "error")}), ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
