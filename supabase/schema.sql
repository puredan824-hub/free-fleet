-- 免费牛马舰队 · Supabase 建表（在 Supabase SQL Editor 整段执行一次）
-- 状态只存一处: 任务队列 + 舰队事件 + 运行结果

create table if not exists fleet_jobs (
  id          bigint generated always as identity primary key,
  kind        text not null,                 -- 例: gpu-batch / scrape / summarize / backup
  payload     jsonb not null default '{}',
  assigned_to text,                          -- kaggle / colab / cloady / ghactions ...
  status      text not null default 'queued'
              check (status in ('queued','running','done','failed')),
  result      jsonb,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create table if not exists fleet_events (
  id          bigint generated always as identity primary key,
  service     text not null,                 -- fleet.yaml 里的 id
  event       text not null,                 -- health-ok / health-fail / quota-warn / keepalive ...
  detail      jsonb not null default '{}',
  created_at  timestamptz not null default now()
);

create index if not exists idx_jobs_status on fleet_jobs (status, created_at);
create index if not exists idx_events_service on fleet_events (service, created_at desc);

-- 保活: Actions 每 3 天插入一条 keepalive 事件, 防 7 天闲置暂停
-- insert into fleet_events (service, event) values ('supabase', 'keepalive');
