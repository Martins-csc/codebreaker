-- Mission v1.2.7 / Micro-Hotfix: URL capability resume table and security-definer functions
-- Re-run safe: uses create table if not exists, DROP FUNCTION IF EXISTS preamble for all historical signatures, and create or replace function.
-- Bulletproof conventions: parameters use p_ prefix; OUT parameters use o_ prefix; NO table aliases inside bodies; every column fully qualified with public.resume_sessions.<column>; no identifier sharing any name with any column.

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
    using (auth.uid() = public.resume_sessions.user_id);

drop policy if exists "Users may delete own resume sessions" on public.resume_sessions;
create policy "Users may delete own resume sessions"
    on public.resume_sessions for delete
    using (auth.uid() = public.resume_sessions.user_id);

-- Drop every function signature ever shipped to prevent 42P13 conflicts on re-run
drop function if exists public.create_resume_token(uuid, text, text, timestamptz);
drop function if exists public.create_resume_token(uuid, text);
drop function if exists public.create_resume_token(p_uid uuid, p_refresh_token text, p_token_hash text, p_expires_at timestamptz);
drop function if exists public.verify_resume_token(text);
drop function if exists public.verify_resume_token(p_token_hash text);
drop function if exists public.revoke_resume_token(text, uuid);
drop function if exists public.revoke_resume_token(text);
drop function if exists public.revoke_resume_token(p_token_hash text, p_uid uuid);
drop function if exists public.revoke_resume_token(p_token_hash text);
drop function if exists public.prune_expired_resume_sessions();

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
    delete from public.resume_sessions
    where public.resume_sessions.expires_at <= now();

    if p_token_hash is not null then
        insert into public.resume_sessions (token_hash, user_id, refresh_token, expires_at)
        values (p_token_hash, p_uid, p_refresh_token, p_expires_at)
        on conflict (token_hash) do update
        set refresh_token = excluded.refresh_token,
            expires_at = excluded.expires_at,
            last_used_at = now();
    else
        insert into public.resume_sessions (token_hash, user_id, refresh_token, expires_at)
        values (gen_random_uuid()::text, p_uid, p_refresh_token, p_expires_at);
    end if;
end;
$$ language plpgsql;

create or replace function public.verify_resume_token(
    p_token_hash text,
    out user_id uuid,
    out refresh_token text,
    out expires_at timestamptz
)
returns record
security definer
set search_path = public
as $$
begin
    delete from public.resume_sessions
    where public.resume_sessions.expires_at <= now();

    select public.resume_sessions.user_id,
           public.resume_sessions.refresh_token,
           public.resume_sessions.expires_at
    into user_id, refresh_token, expires_at
    from public.resume_sessions
    where public.resume_sessions.token_hash = p_token_hash
      and public.resume_sessions.expires_at > now();

    if found then
        update public.resume_sessions
        set last_used_at = now()
        where public.resume_sessions.token_hash = p_token_hash
          and public.resume_sessions.expires_at > now();
    end if;
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
        where public.resume_sessions.token_hash = p_token_hash
          and public.resume_sessions.user_id = p_uid;
    else
        delete from public.resume_sessions
        where public.resume_sessions.token_hash = p_token_hash;
    end if;
end;
$$ language plpgsql;

create or replace function public.prune_expired_resume_sessions()
returns void
security definer
set search_path = public
as $$
begin
    delete from public.resume_sessions
    where public.resume_sessions.expires_at <= now();
end;
$$ language plpgsql;
