"""poc

Revision ID: 5909ee33095c
Revises:
Create Date: 2022-08-18 21:56:23.761102

"""
import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5909ee33095c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "joby_todo_task",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("kwargs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("todo_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("max_retry_on_failure", sa.Integer(), nullable=True),
        sa.CheckConstraint("created_at <= updated_at"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "joby_todo_task_parents",
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["joby_todo_task.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["joby_todo_task.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("task_id", "parent_id"),
    )

    sa.DDL(
        """CREATE OR REPLACE FUNCTION joby_delete_task ()
        returns TRIGGER LANGUAGE plpgsql
        AS $$
            BEGIN
                DELETE FROM joby_todo_task WHERE id = OLD.task_id;
                RETURN NULL;
            END;
        $$;
    """
    ).execute(bind=op.get_bind(), target=None)

    sa.DDL(
        """CREATE TRIGGER drop_orphan_task
        AFTER DELETE ON joby_todo_task_parents FOR EACH ROW
        EXECUTE FUNCTION joby_delete_task()
    """
    ).execute(bind=op.get_bind(), target=None)


def downgrade() -> None:
    sa.DDL("DROP FUNCTION joby_delete_task;").execute(bind=op.get_bind(), target=None)
    sa.DDL("DROP TRIGGER drop_orphan_task ON joby_todo_task_parents;").execute(bind=op.get_bind(), target=None)

    op.drop_table("joby_todo_task_parents")
    op.drop_table("joby_todo_task")
