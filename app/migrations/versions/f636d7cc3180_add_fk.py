from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f636d7cc3180'
down_revision: Union[str, None] = 'd73b54943847'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the constraint only if it exists
    conn = op.get_bind()
    result = conn.execute(
        "SELECT conname FROM pg_constraint WHERE conname = 'unique_receipt_id';"
    )
    if result.rowcount > 0:
        op.drop_constraint('unique_receipt_id', 'payments', type_='unique')

    # Add the new column and foreign key
    op.add_column('subscriptions', sa.Column('payment_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'subscriptions', 'payments', ['payment_id'], ['id'])


def downgrade() -> None:
    # Drop the foreign key and column
    op.drop_constraint(None, 'subscriptions', type_='foreignkey')
    op.drop_column('subscriptions', 'payment_id')

    # Recreate the unique constraint
    op.create_unique_constraint('unique_receipt_id', 'payments', ['receipt_id'])
