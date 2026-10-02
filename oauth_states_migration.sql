-- Mission v1.5.5: OAuth states table for manual PKCE flow
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
