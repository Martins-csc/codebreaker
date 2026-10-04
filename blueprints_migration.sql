-- Mission v1.5.0: Persistent Blueprint Library table and RLS policies
-- Mission v1.6.0: Added versioning (version, parent_id)
create table if not exists public.blueprints (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    title text not null,
    blueprint_json jsonb not null,
    version integer default 1,
    parent_id uuid,
    created_at timestamptz default now()
);

-- Ensure columns exist if table already created
ALTER TABLE public.blueprints ADD COLUMN IF NOT EXISTS version integer DEFAULT 1;
ALTER TABLE public.blueprints ADD COLUMN IF NOT EXISTS parent_id uuid;

alter table public.blueprints enable row level security;

drop policy if exists "Users may select own blueprints" on public.blueprints;
create policy "Users may select own blueprints"
    on public.blueprints for select
    using (auth.uid() = public.blueprints.user_id);

drop policy if exists "Users may insert own blueprints" on public.blueprints;
create policy "Users may insert own blueprints"
    on public.blueprints for insert
    with check (auth.uid() = public.blueprints.user_id);

drop policy if exists "Users may delete own blueprints" on public.blueprints;
create policy "Users may delete own blueprints"
    on public.blueprints for delete
    using (auth.uid() = public.blueprints.user_id);

drop policy if exists "Users may update own blueprints" on public.blueprints;
create policy "Users may update own blueprints"
    on public.blueprints for update
    using (auth.uid() = public.blueprints.user_id);
