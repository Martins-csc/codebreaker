-- Mission v1.5.5: OAuth states table for manual PKCE flow
-- Mission v1.9.9: Added consume_oauth_state RPC for consume-once verifier enforcement
create table if not exists public.oauth_states (
    state text primary key,
    code_verifier text not null,
    created_at timestamptz default now()
);

alter table public.oauth_states enable row level security;

drop policy if exists "Allow public insert oauth_states" on public.oauth_states;
create policy "Allow public insert oauth_states"
    on public.oauth_states for insert
    to public
    with check (true);

drop policy if exists "Allow public select oauth_states" on public.oauth_states;
create policy "Allow public select oauth_states"
    on public.oauth_states for select
    to public
    using (true);

drop policy if exists "Allow public delete oauth_states" on public.oauth_states;
create policy "Allow public delete oauth_states"
    on public.oauth_states for delete
    to public
    using (true);

drop function if exists public.consume_oauth_state(text);
create or replace function public.consume_oauth_state(p_state text)
returns table (code_verifier text)
security definer
set search_path = public
as $$
begin
    delete from public.oauth_states
    where public.oauth_states.created_at < (now() - interval '10 minutes');

    return query
    delete from public.oauth_states
    where public.oauth_states.state = p_state
    returning public.oauth_states.code_verifier;
end;
$$ language plpgsql;
