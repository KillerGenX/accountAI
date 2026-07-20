"""create_workspace_requests_and_trigger

Revision ID: f3f9be4a991b
Revises: 4ae9471983ae
Create Date: 2026-07-20 12:52:00.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f3f9be4a991b'
down_revision: Union[str, Sequence[str], None] = '4ae9471983ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create workspace_requests table
    op.create_table(
        'workspace_requests',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspace_requests_email'), 'workspace_requests', ['email'], unique=True)

    # 2. Define Postgres Trigger Function & Trigger for automatic workspace creation on ACC
    trigger_function_sql = """
    CREATE OR REPLACE FUNCTION handle_workspace_approval()
    RETURNS TRIGGER AS $$
    DECLARE
        v_workspace_id UUID;
        v_user_id UUID;
    BEGIN
        IF NEW.status = 'approved' AND OLD.status = 'pending' THEN
            -- 1. Create Workspace
            v_workspace_id := gen_random_uuid();
            INSERT INTO workspaces (id, name, company_name, industry, timezone, currency, status, created_at, updated_at)
            VALUES (v_workspace_id, NEW.company_name, NEW.company_name, NEW.industry, 'Asia/Jakarta', 'IDR', 'active', now(), now());

            -- 2. Initialize 3 default AI employees
            INSERT INTO employee_configs (id, workspace_id, employee_name, is_enabled, config, updated_at)
            VALUES 
                (gen_random_uuid(), v_workspace_id, 'AccountDiscoveryEmployee', true, '{}'::jsonb, now()),
                (gen_random_uuid(), v_workspace_id, 'CompanyResearchEmployee', true, '{}'::jsonb, now()),
                (gen_random_uuid(), v_workspace_id, 'BuyingSignalEmployee', true, '{}'::jsonb, now());

            -- 3. Create Pending User
            v_user_id := gen_random_uuid();
            INSERT INTO users (id, workspace_id, email, full_name, role, status, created_at, updated_at)
            VALUES (v_user_id, v_workspace_id, NEW.email, NEW.full_name, 'administrator', 'pending', now(), now());

            -- 4. Create empty UserSettings
            INSERT INTO user_settings (id, user_id, workspace_id, notification_preferences, display_preferences, created_at, updated_at)
            VALUES (gen_random_uuid(), v_user_id, v_workspace_id, '{}'::jsonb, '{}'::jsonb, now(), now());
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """

    trigger_sql = """
    CREATE TRIGGER trg_workspace_approval
    AFTER UPDATE ON workspace_requests
    FOR EACH ROW
    EXECUTE FUNCTION handle_workspace_approval();
    """

    op.execute(sa.text(trigger_function_sql))
    op.execute(sa.text(trigger_sql))


def downgrade() -> None:
    # 1. Drop trigger and trigger function
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_workspace_approval ON workspace_requests;"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS handle_workspace_approval();"))

    # 2. Drop table and index
    op.drop_index(op.f('ix_workspace_requests_email'), table_name='workspace_requests')
    op.drop_table('workspace_requests')
