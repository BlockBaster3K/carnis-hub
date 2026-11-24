#!/usr/bin/env python3
"""Дождаться завершения CI-прогона и напечатать сводку + итоговый SHA-256 jar."""
import json, os, sys, time, urllib.request, hashlib

RUN_ID = sys.argv[1] if len(sys.argv) > 1 else "45495330254"
TOK = os.environ.get("GITHUB_TOKEN", "").strip()
API = "https://api.github.com/repos/BlockBaster3K/carnis-hub"


def get(url, raw=False):
    r = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOK}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(r) as resp:
        data = resp.read()
    return data if raw else json.loads(data or b"{}")


deadline = time.time() + 1800
run = {}
while time.time() < deadline:
    run = get(f"{API}/actions/runs/{RUN_ID}")
    print(f"[{time.strftime('%H:%M:%S')}] {run['status']} / {run['conclusion']}", flush=True)
    if run["status"] == "completed":
        break
    time.sleep(15)

if run.get("status") != "completed":
    print("ТАЙМАУТ: прогон не завершился")
    sys.exit(1)

print(f"\n=== run {RUN_ID}: {run['conclusion']} · {run['head_sha']} ===")
jobs = get(f"{API}/actions/runs/{RUN_ID}/jobs")["jobs"]
for j in jobs:
    print(f"  job {j['name']}: {j['status']}/{j['conclusion']}")
    for s in j.get("steps", []):
        mark = {"success": "✓", "failure": "✗", "skipped": "–", "cancelled": "⊘"}.get(s["conclusion"], " ")
        print(f"    {mark} {s['name']}")

if run["conclusion"] != "success":
    print("\nПРОГОН НЕУСПЕШЕН — логи:")
    try:
        logs = get(f"{API}/actions/runs/{RUN_ID}/logs", raw=True)
        with open("/tmp/run_logs.zip", "wb") as f:
            f.write(logs)
        print("  сохранено в /tmp/run_logs.zip")
    except Exception as e:
        print("  логи недоступны:", e)
    sys.exit(1)

# Итоговый jar: сначала из коммитов main, затем из релизов.
print("\n=== последние коммиты main ===")
for c in get(f"{API}/commits?sha=main&per_page=4")[:4]:
    print(f"  {c['sha'][:8]}  {c['commit']['message'].splitlines()[0][:88]}")

for url, label in [
    (f"{API}/contents/06-build/jars/carnis-3.5.2.jar?ref=main", "06-build/jars/carnis-3.5.2.jar"),
    (f"{API}/releases/tags/v3.5.2", "release v3.5.2"),
]:
    try:
        data = get(url)
        if "assets" in data:
            for a in data["assets"]:
                print(f"  asset {a['name']}: {a['size']} Б, url {a['browser_download_url']}")
        else:
            blob = get(data["download_url"], raw=True)
            print(f"  {label}: {len(blob)} Б, sha256 {hashlib.sha256(blob).hexdigest()}")
            open("/home/user/carnis-3.5.2.jar", "wb").write(blob)
    except Exception as e:
        print(f"  {label}: не удалось получить — {e}")
