-- HallHop minimal schema (no JWT/session/auth tables)

create extension if not exists pgcrypto;

create table if not exists public.checkouts (
  id uuid primary key default gen_random_uuid(),
  student_id text not null,
  student_name text not null,
  class_name text not null,
  period smallint not null check (period between 1 and 8),
  room text,
  teacher text,
  checkout_time timestamptz not null,
  checkin_time timestamptz,
  duration_sec integer check (duration_sec is null or duration_sec >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_checkouts_student_id on public.checkouts(student_id);
create index if not exists idx_checkouts_checkout_time on public.checkouts(checkout_time desc);
create index if not exists idx_checkouts_open on public.checkouts(student_id) where checkin_time is null;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_checkouts_set_updated_at on public.checkouts;
create trigger trg_checkouts_set_updated_at
before update on public.checkouts
for each row
execute function public.set_updated_at();

-- Bare minimum: disable RLS to avoid auth coupling
alter table public.checkouts disable row level security;
