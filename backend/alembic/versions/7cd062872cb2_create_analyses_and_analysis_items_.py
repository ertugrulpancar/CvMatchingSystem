"""create analyses and analysis_items tables

Revision ID: 7cd062872cb2
Revises:
Create Date: 2026-09-25 13:15:26.085173

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7cd062872cb2"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# PLAN.md §3b/§7: FK'ler auth.users'a (Alembic'in sahip olmadığı bir şema) ve
# RLS enable komutları burada ham SQL (op.execute) ile yazılır.
UPGRADE_SQL = """
create table public.analyses (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  created_at      timestamptz not null default now(),
  job_title       text,
  company_name    text,
  job_text        text not null,
  cv_source       text not null check (cv_source in ('pdf','docx','text')),
  overall_score   smallint not null check (overall_score between 0 and 100),
  output_language text not null check (output_language in ('tr','en')),
  matcher         text not null check (matcher in ('llm','keyword')),
  model           text,
  duration_ms     integer not null
);
create index analyses_user_created_idx on public.analyses (user_id, created_at desc);

create table public.analysis_items (
  id               uuid primary key default gen_random_uuid(),
  analysis_id      uuid not null references public.analyses(id) on delete cascade,
  position         smallint not null,
  requirement_text text not null,
  category         text not null check (
                     category in (
                       'technical_skill','tool','experience','education','language','soft_skill'
                     )
                   ),
  importance       text not null check (importance in ('must_have','nice_to_have')),
  status           text not null check (status in ('met','partial','missing')),
  evidence         text,
  explanation      text not null
);
create index analysis_items_analysis_idx on public.analysis_items (analysis_id);

alter table public.analyses       enable row level security;
alter table public.analysis_items enable row level security;
-- Politika YOK: anon/authenticated rolleri PostgREST üzerinden hiçbir şey
-- okuyamaz/yazamaz. Backend, RLS'ten etkilenmeyen postgres rolüyle bağlanır.
"""

DOWNGRADE_SQL = """
drop table if exists public.analysis_items;
drop table if exists public.analyses;
"""


def upgrade() -> None:
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    op.execute(DOWNGRADE_SQL)
