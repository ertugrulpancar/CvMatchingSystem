"""enable rls on alembic_version

Revision ID: f90dcb2bca0e
Revises: 7cd062872cb2
Create Date: 2026-09-25 13:37:09.028003

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f90dcb2bca0e"
down_revision: str | Sequence[str] | None = "7cd062872cb2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# alembic_version, public şemasında olduğu için PostgREST/anon key'e açık.
# İçinde hassas veri yok ama projenin "her tabloda RLS açık, politikasız"
# ilkesiyle tutarlı olsun diye burada da kapatıyoruz (Supabase security
# advisor'ının rls_disabled_in_public bulgusuna karşılık).
UPGRADE_SQL = "alter table public.alembic_version enable row level security;"
DOWNGRADE_SQL = "alter table public.alembic_version disable row level security;"


def upgrade() -> None:
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    op.execute(DOWNGRADE_SQL)
