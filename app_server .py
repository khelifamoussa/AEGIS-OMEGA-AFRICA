import json
import os
import sys
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(ROOT, "ui")
sys.path.insert(0, ROOT)

import aegis_v8 as aegis

HOST = "127.0.0.1"
PORT = 8765


def build_result(payload):
    data = aegis.DEFAULT_SCENARIO.copy()
    data.update(payload or {})

    errors = aegis.validate_input(data)
    if errors:
        return {"ok": False, "errors": errors}

    started = time.perf_counter()
    plan = aegis.build_safe_plan(data)
    immediate = time.perf_counter() - started

    score = aegis.severity_score(data)
    label = aegis.severity_label(score)
    confidence = aegis.calculate_rule_confidence(data)

    return {
        "ok": True,
        "system": "AEGIS OMEGA AFRICA",
        "version": aegis.VERSION,
        "status": "VERIFIED",
        "severity": {"label": label, "score": score},
        "rule_confidence": confidence,
        "immediate_decision_sec": immediate,
        "ai_status": "DETERMINISTIC SAFE MODE",
        "model": "Qwen3-4B / llama.cpp (optional)",
        "decision": plan,
        "input": data,
    }


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = urlparse(path).path
        if path == "/":
            path = "/index.html"
        return os.path.join(UI_DIR, path.lstrip("/"))

    def send_json(self, obj, status=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path.startswith("/api/health"):
            return self.send_json({
                "ok": True,
                "status": "ACTIVE",
                "engine": aegis.VERSION,
                "offline": True
            })
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/analyze"):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                payload = json.loads(body.decode("utf-8")) if body else {}
                result = build_result(payload)
                return self.send_json(result, 200 if result.get("ok") else 400)
            except Exception as exc:
                return self.send_json(
                    {"ok": False, "errors": [str(exc)]},
                    500
                )

        return self.send_json(
            {"ok": False, "errors": ["Unknown endpoint"]},
            404
        )

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    os.chdir(UI_DIR)
    print("=" * 68)
    print("AEGIS OMEGA AFRICA - LIVE LOCAL UI")
    print(f"Engine : {aegis.VERSION}")
    print(f"Open   : http://{HOST}:{PORT}")
    print("=" * 68)
    print("Keep this window open while using the interface.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
