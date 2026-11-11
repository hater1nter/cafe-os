"""Initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-11-11 21:06:43.958000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    op.execute("""
        CREATE TYPE orderstatus AS ENUM (
            'received', 'confirmed', 'preparing', 'almost_ready', 'ready', 'completed', 'cancelled'
        )
    """)
    op.execute("""
        CREATE TYPE ordertype AS ENUM (
            'takeaway', 'dine_in', 'delivery'
        )
    """)
    op.execute("""
        CREATE TYPE paymentstatus AS ENUM (
            'pending', 'paid', 'failed', 'refunded'
        )
    """)
    op.execute("""
        CREATE TYPE loyaltytier AS ENUM (
            'bronze', 'silver', 'gold', 'black'
        )
    """)
    op.execute("""
        CREATE TYPE staffrole AS ENUM (
            'admin', 'manager', 'barista', 'customer_support'
        )
    """)

    # organizations table
    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('branding', postgresql.JSON(), nullable=True),
        sa.Column('subscription_tier', sa.String(50), nullable=True),
        sa.Column('telegram_bot_token', sa.String(255), nullable=True),
        sa.Column('payment_provider', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('telegram_bot_token')
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'])
    op.create_index('ix_organizations_id', 'organizations', ['id'])

    # branches table
    op.create_table('branches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('operating_hours', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_branches_organization_id', 'branches', ['organization_id'])

    # users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_id', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('preferred_language', sa.String(10), nullable=True),
        sa.Column('registration_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])
    op.create_index('ix_users_organization_id', 'users', ['organization_id'])

    # categories table
    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # products table
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('nutritional_info', postgresql.JSON(), nullable=True),
        sa.Column('allergens', postgresql.JSON(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('is_seasonal', sa.Boolean(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_organization_id', 'products', ['organization_id'])

    # modifiers table
    op.create_table('modifiers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('options', postgresql.JSON(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_modifiers_product_id', 'modifiers', ['product_id'])

    # orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False),
        sa.Column('status', orderstatus, nullable=True),
        sa.Column('order_type', ordertype, nullable=False),
        sa.Column('table_number', sa.String(50), nullable=True),
        sa.Column('items', postgresql.JSON(), nullable=False),
        sa.Column('subtotal', sa.Integer(), nullable=False),
        sa.Column('tax', sa.Integer(), nullable=True),
        sa.Column('discount', sa.Integer(), nullable=True),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.Column('payment_status', paymentstatus, nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_provider_transaction_id', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('estimated_time', sa.Integer(), nullable=True),
        sa.Column('ready_eta', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_order_number', 'orders', ['order_number'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_organization_id', 'orders', ['organization_id'])
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])
    op.create_index('ix_orders_payment_status', 'orders', ['payment_status'])

    # order_status_history table
    op.create_table('order_status_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', orderstatus, nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('changed_by', sa.String(255), nullable=True),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_status_history_order_id', 'order_status_history', ['order_id'])

    # loyalty_accounts table
    op.create_table('loyalty_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tier', loyaltytier, nullable=True),
        sa.Column('points_balance', sa.Integer(), nullable=True),
        sa.Column('last_reset_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_loyalty_accounts_user_id', 'loyalty_accounts', ['user_id'])
    op.create_index('ix_loyalty_accounts_organization_id', 'loyalty_accounts', ['organization_id'])

    # loyalty_transactions table
    op.create_table('loyalty_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loyalty_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reference_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['loyalty_account_id'], ['loyalty_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_loyalty_transactions_loyalty_account_id', 'loyalty_transactions', ['loyalty_account_id'])

    # staff table
    op.create_table('staff',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('telegram_id', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('role', staffrole, nullable=False),
        sa.Column('permissions', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('ix_staff_organization_id', 'staff', ['organization_id'])
    op.create_index('ix_staff_branch_id', 'staff', ['branch_id'])


def downgrade() -> None:
    op.drop_index('ix_staff_branch_id', table_name='staff')
    op.drop_index('ix_staff_organization_id', table_name='staff')
    op.drop_table('staff')

    op.drop_index('ix_loyalty_transactions_loyalty_account_id', table_name='loyalty_transactions')
    op.drop_table('loyalty_transactions')

    op.drop_index('ix_loyalty_accounts_organization_id', table_name='loyalty_accounts')
    op.drop_index('ix_loyalty_accounts_user_id', table_name='loyalty_accounts')
    op.drop_table('loyalty_accounts')

    op.drop_index('ix_order_status_history_order_id', table_name='order_status_history')
    op.drop_table('order_status_history')

    op.drop_index('ix_orders_payment_status', table_name='orders')
    op.drop_index('ix_orders_created_at', table_name='orders')
    op.drop_index('ix_orders_user_id', table_name='orders')
    op.drop_index('ix_orders_organization_id', table_name='orders')
    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_order_number', table_name='orders')
    op.drop_table('orders')

    op.drop_index('ix_modifiers_product_id', table_name='modifiers')
    op.drop_table('modifiers')

    op.drop_index('ix_products_organization_id', table_name='products')
    op.drop_table('products')

    op.drop_table('categories')

    op.drop_index('ix_users_organization_id', table_name='users')
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_table('users')

    op.drop_index('ix_branches_organization_id', table_name='branches')
    op.drop_table('branches')

    op.drop_index('ix_organizations_id', table_name='organizations')
    op.drop_index('ix_organizations_slug', table_name='organizations')
    op.drop_table('organizations')

    op.execute("DROP TYPE staffrole")
    op.execute("DROP TYPE loyaltytier")
    op.execute("DROP TYPE paymentstatus")
    op.execute("DROP TYPE ordertype")
    op.execute("DROP TYPE orderstatus")
