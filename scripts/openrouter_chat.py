#!/usr/bin/env python3
"""OpenRouter 轻量调用: 自动从 /models 挑当前 :free 模型, 单次短问答。
密钥只从环境变量 OPENROUTER_API_KEY 读, 绝不落文件。
预算闸: 本脚本每次运行只发 1 次请求; 每日 <=45 次由调用方 (Actions/Cloady) 计数。
用法: OPENROUTER_API_KEY=... python3 openrouter_chat.py "把这段话总结成一句: ..."
"""
import json, os, sys, urllib.request

API = "https://openrouter.ai/api/v1"

def call(path, payload=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode() if payload else None,
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        },
        method="POST" if payload else "GET",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def pick_free_model():
    models = call("/models")["data"]
    free = [m["id"] for m in models if m["id"].endswith(":free")]
    if not free:
        raise SystemExit("当前没有 :free 模型可用 (名单每月轮换)")
    return free[0]

def main():
    if "OPENROUTER_API_KEY" not in os.environ:
        raise SystemExit("缺 OPENROUTER_API_KEY 环境变量")
    prompt = " ".join(sys.argv[1:]) or "say ok"
    model = pick_free_model()
    out = call("/chat/completions", {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
    })
    print(json.dumps({"model": model, "reply": out["choices"][0]["message"]["content"]},
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
