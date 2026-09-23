-- Mission v1.2.5 / Micro-Hotfix: URL capability resume table and security-definer functions
-- Re-run safe: uses create table if not exists, create or replace function, and omits drop table.
-- All function parameters and RETURNS TABLE out-params use p_ prefix (p_token_hash, p_user_id, p_refresh_token, p_expires_at, p_uid).
-- Parameter renaming is the only durable fix for Postgres 42702; variable_conflict pragmas banned.
-- Every table column reference fully qualified with resume_sessions. or rs.

create table if not exists public.resume_sessions (
    id uuid primary key default gen_random_uuid(),
    token_hash text unique not null,
    user_id uuid not null,
    refresh_token text not null,
    created_at timestamptz default now(),
    expires_at timestamptz not null,
    last_used_at timestamptz default now()
);

alter table public.resume_sessions enable row level security;

drop policy if exists "Users may select own resume sessions" on public.resume_sessions;
create policy "Users may select own resume sessions"
    on public.resume_sessions for select
    using (auth.uid() = resume_sessions.user_id);

drop policy if exists "Users may delete own resume sessions" on public.resume_sessions;
create policy "Users may delete own resume sessions"
    on public.resume_sessions for delete
    using (auth.uid() = resume_sessions.user_id);

create or replace function public.create_resume_token(
    p_uid uuid,
    p_refresh_token text,
    p_token_hash text default null,
    p_expires_at timestamptz default (now() + interval '7 days')
)
returns void
security definer
set search_path = public
as $$
begin
    -- Opportunistic prune of expired tokens (fully qualified column reference)
    delete from public.resume_sessions where resume_sessions.expires_at <= now();

    if p_token_hash is not null then
        insert into public.resume_sessions (token_hash, user_id, refresh_token, expires_at)
        values (p_token_hash, p_uid, p_refresh_token, p_expires_at)
        on conflict (token_hash) do update
        set resume_sessions.refresh_token = excluded.refresh_token,
            resume_sessions.expires_at = excluded.expires_at,
            last_used_at = now();
    else
        -- If called with just uid and refresh_token, store with a generated hash or handle
        insert into public.resume_sessions (token_hash, user_id, refresh_token, expires_at)
        values (gen_random_uuid()::text, p_uid, p_refresh_token, p_expires_at);
    end if;
end;
$$ language plpgsql;

create or replace function public.verify_resume_token(
    p_token_hash text
)
returns table (
    p_user_id uuid,
    p_refresh_token text,
    p_expires_at timestamptz
)
security definer
set search_path = public
as $$
begin
    -- Prune expired tokens opportunistically
    delete from public.resume_sessions where resume_sessions.expires_at <= now();

    return query
    select rs.user_id, rs.refresh_token, rs.expires_at
    from public.resume_sessions rs
    where rs.token_hash = p_token_hash
      and rs.expires_at > now();

    update public.resume_sessions
    set last_used_at = now()
    where resume_sessions.token_hash = p_token_hash
      and resume_sessions.expires_at > now();
end;
$$ language plpgsql;

create or replace function public.revoke_resume_token(
    p_token_hash text,
    p_uid uuid default null
)
returns void
security definer
set search_path = public
as $$
begin
    if p_uid is not null then
        delete from public.resume_sessions
        where resume_sessions.token_hash = p_token_hash 
          and resume_sessions.user_id = p_uid;
    else
        delete from public.resume_sessions
        where resume_sessions.token_hash = p_token_hash;
    end if;
end;
$$ language plpgsql;

create or replace function public.prune_expired_resume_sessions()
returns void
security definer
set search_path = public
as $$
begin
    delete from public.resume_sessions where resume_sessions.expires_at <= now();
end;
$$ language plpgsql;
