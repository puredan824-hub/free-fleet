// 免费牛马舰队 · Cloudflare Worker 边缘网关
// 职责: 对外唯一入口。/health 自检, /webhook 收事件写 Supabase, 其余 404。
// 环境变量 (wrangler secret / dashboard): SUPABASE_URL, SUPABASE_SERVICE_KEY, WEBHOOK_TOKEN
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({ ok: true, service: "free-fleet-gateway", ts: new Date().toISOString() });
    }

    if (url.pathname === "/webhook" && request.method === "POST") {
      if (request.headers.get("x-fleet-token") !== env.WEBHOOK_TOKEN) {
        return Response.json({ ok: false, error: "unauthorized" }, { status: 401 });
      }
      const body = await request.json().catch(() => null);
      if (!body || !body.service || !body.event) {
        return Response.json({ ok: false, error: "service and event required" }, { status: 400 });
      }
      const res = await fetch(`${env.SUPABASE_URL}/rest/v1/fleet_events`, {
        method: "POST",
        headers: {
          apikey: env.SUPABASE_SERVICE_KEY,
          Authorization: `Bearer ${env.SUPABASE_SERVICE_KEY}`,
          "Content-Type": "application/json",
          Prefer: "return=minimal",
        },
        body: JSON.stringify({ service: body.service, event: body.event, detail: body.detail || {} }),
      });
      return Response.json({ ok: res.ok }, { status: res.ok ? 202 : 502 });
    }

    return Response.json({ ok: false, error: "not found" }, { status: 404 });
  },
};
