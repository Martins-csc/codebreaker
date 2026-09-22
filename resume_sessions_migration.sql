-- Mission v1.2.3: URL capability resume table and security-definer functions

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
    using (auth.uid() = user_id);

drop policy if exists "Users may delete own resume sessions" on public.resume_sessions;
create policy "Users may delete own resume sessions"
    on public.resume_sessions for delete
    using (auth.uid() = user_id);

create or replace function public.create_resume_token(
    uid uuid,
    refresh_token text,
    token_hash text default null,
    expires_at timestamptz default (now() + interval '7 days')
)
returns void
security definer
set search_path = public
as $$
begin
    -- Opportunistic prune of expired tokens
    delete from public.resume_sessions where expires_at <= now();

    if token_hash is not null then
        insert into public.resume_sessions (token_hash, user_id, refresh_token, expires_at)
        values (token_hash, uid, refresh_token, expires_at)
        on conflict (token_hash) do update
        set refresh_token = excluded.refresh_token,
            expires_at = excluded.expires_at,
            last_used_at = now();
    else
        -- If called with just uid and refresh_token, store with a generated hash or handle
        insert into public.resume_sessions (token_hash, user_id, refresh_token, expires_at)
        values (gen_random_uuid()::text, uid, refresh_token, expires_at);
    end if;
end;
$$ language plpgsql;

create or replace function public.verify_resume_token(
    token_hash text
)
returns table (
    user_id uuid,
    refresh_token text,
    expires_at timestamptz
)
security definer
set search_path = public
as $$
begin
    -- Prune expired tokens opportunistically
    delete from public.resume_sessions where expires_at <= now();

    return query
    select rs.user_id, rs.refresh_token, rs.expires_at
    from public.resume_sessions rs
    where rs.token_hash = verify_resume_token.token_hash
      and rs.expires_at > now();

    update public.resume_sessions
    set last_used_at = now()
    where resume_sessions.token_hash = verify_resume_token.token_hash
      and resume_sessions.expires_at > now();
end;
$$ language plpgsql;

create or replace function public.revoke_resume_token(
    token_hash text,
    uid uuid default null
)
returns void
security definer
set search_path = public
as $$
begin
    if uid is not null then
        delete from public.resume_sessions
        where resume_sessions.token_hash = revoke_resume_token.token_hash 
          and resume_sessions.user_id = revoke_resume_token.uid;
    else
        delete from public.resume_sessions
        where resume_sessions.token_hash = revoke_resume_token.token_hash;
    end if;
end;
$$ language plpgsql;

create or replace function public.prune_expired_resume_sessions()
returns void
security definer
set search_path = public
as $$
begin
    delete from public.resume_sessions where expires_at <= now();
end;
$$ language plpgsql;
