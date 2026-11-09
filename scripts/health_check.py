#!/usr/bin/env python3
"""舰队健康巡检: 读 fleet-endpoints.json, 逐个探活, 输出 JSON 结论。
无第三方依赖 (stdlib only)。端点未配置的记为 pending, 不算故障。
用法: python3 health_check.py [endpoints.json]
"""
import json, sys, urllib.request, urllib.error
from datetime import datetime, timezone

def probe(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-fleet-health/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"ok": 200 <= r.status < 400, "status": r.status}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": str(e)}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e)[:200]}

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "fleet-endpoints.json"
    try:
        cfg = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        cfg = {}
    results = {}
    for service, url in sorted(cfg.items()):
        if not url:
            results[service] = {"ok": None, "note": "pending-config"}
        else:
            results[service] = probe(url)
    out = {"checked_at": datetime.now(timezone.utc).isoformat(), "results": results}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    bad = [k for k, v in results.items() if v.get("ok") is False]
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
