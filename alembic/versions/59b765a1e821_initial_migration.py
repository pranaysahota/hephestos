"""Initial migration

Revision ID: 59b765a1e821
Revises: 
Create Date: 2024-06-03 23:26:59.017672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59b765a1e821'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    CREATE TYPE data_type AS ENUM ('int', 'string', 'datetime');
    CREATE TYPE comparison_operator AS ENUM ('=', '<', '>', '<=', '>=');
    CREATE TYPE condition_type AS ENUM ('if', 'switch', 'if-elseif');
    CREATE TYPE node_type AS ENUM ('condition', 'action', 'trigger', 'http', 'delay', 'integration');
    CREATE TYPE execution_state AS ENUM ('NEW', 'IN_PROGRESS', 'PAUSE', 'COMPLETE', 'RETRY');
    CREATE TYPE status AS ENUM ('FAILED', 'SUCCESS', 'RUNNING');
    
    CREATE TABLE customers (
        id SERIAL PRIMARY KEY,
        customer_id INT NOT NULL,
        shop_id INT NOT NULL,
        email VARCHAR(255) NOT NULL,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        state VARCHAR(50),
        verified_email BOOLEAN,
        email_marketing_consent JSONB
    );
    
    CREATE TABLE shops (
        shop_id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        total_price NUMERIC(10, 2) NOT NULL,
        shop_id INT NOT NULL,
        customer_id INT NOT NULL,
        payload JSONB
    );
    
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        price NUMERIC(10, 2) NOT NULL
    );
    
    CREATE TABLE webhooks_subscribed (
        id SERIAL PRIMARY KEY,
        webhook_topic VARCHAR(255) NOT NULL
    );
    
    CREATE TABLE integrators (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        config_file_path VARCHAR(255) NOT NULL
    );
    
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        is_admin BOOLEAN
    );
    
    CREATE TABLE templates (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT
    );
    
    CREATE TABLE templates_shop_mapping (
        template_id INT NOT NULL,
        shop_id INT NOT NULL,
        FOREIGN KEY (template_id) REFERENCES templates(id),
        FOREIGN KEY (shop_id) REFERENCES shops(shop_id)
    );
    
    CREATE TABLE automations (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        user_id INT NOT NULL,
        shop_id INT NOT NULL,
        webhook_id INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (shop_id) REFERENCES shops(shop_id)
    );
    
    CREATE TABLE nodes (
        id SERIAL PRIMARY KEY,
        node_type node_type NOT NULL,
        auto_id INT NOT NULL,
        FOREIGN KEY (auto_id) REFERENCES automations(id)
    );
    
    CREATE TABLE edges (
        from_node_id INT NOT NULL,
        to_node_id INT,
        FOREIGN KEY (from_node_id) REFERENCES nodes(id),
        FOREIGN KEY (to_node_id) REFERENCES nodes(id)
    );
    
    CREATE TABLE fields (
        id SERIAL PRIMARY KEY,
        field_name VARCHAR(255) NOT NULL,
        type data_type NOT NULL
    );
    
    CREATE TABLE nodes_fields_mapping (
        node_id INT NOT NULL,
        field_id INT NOT NULL,
        FOREIGN KEY (node_id) REFERENCES nodes(id),
        FOREIGN KEY (field_id) REFERENCES fields(id)
    );
    
    CREATE TABLE condition_nodes (
        node_id INT NOT NULL,
        condition_type condition_type NOT NULL,
        sequence INT NOT NULL,
        operator comparison_operator NOT NULL,
        operand1 INT NOT NULL,
        operand2 VARCHAR(255),
        FOREIGN KEY (node_id) REFERENCES nodes(id),
        FOREIGN KEY (operand1) REFERENCES fields(id)
    );
    
    CREATE TABLE condition_node_mapping (
        node_id INT NOT NULL,
        eval BOOLEAN NOT NULL,
        next_node_id INT,
        FOREIGN KEY (node_id) REFERENCES nodes(id),
        FOREIGN KEY (next_node_id) REFERENCES nodes(id)
    );
    
    CREATE TABLE delay_nodes (
        node_id INT NOT NULL,
        delay_period INT NOT NULL,
        FOREIGN KEY (node_id) REFERENCES nodes(id)
    );
    
    CREATE TABLE integrator_nodes (
        node_id INT NOT NULL,
        integrator_id INT NOT NULL,
        context JSONB,
        FOREIGN KEY (node_id) REFERENCES nodes(id),
        FOREIGN KEY (integrator_id) REFERENCES integrators(id)
    );
    
    CREATE TABLE http_nodes (
        node_id INT NOT NULL,
        http_method VARCHAR(10) NOT NULL,
        http_url VARCHAR(255) NOT NULL,
        FOREIGN KEY (node_id) REFERENCES nodes(id)
    );
    
    -- Comment on these tables is "EXECUTION_TABLES"
    
    CREATE TABLE workflow_execution (
        id SERIAL PRIMARY KEY,
        state execution_state NOT NULL,
        curr_node_id INT NOT NULL,
        auto_id INT NOT NULL,
        retry BOOLEAN,
        status status NOT NULL,
        start_time TIMESTAMP DEFAULT NOW(),
        update_time TIMESTAMP,
        end_time TIMESTAMP,
        FOREIGN KEY (curr_node_id) REFERENCES nodes(id)
    );
    
    CREATE TABLE node_execution (
        id SERIAL PRIMARY KEY,
        node_id INT NOT NULL,
        next_node_id INT,
        workflow_id INT NOT NULL,
        state execution_state NOT NULL,
        start_time TIMESTAMP DEFAULT NOW(),
        end_time TIMESTAMP,
        retry BOOLEAN,
        FOREIGN KEY (node_id) REFERENCES nodes(id),
        FOREIGN KEY (next_node_id) REFERENCES nodes(id),
        FOREIGN KEY (workflow_id) REFERENCES workflow_execution(id)
    );
    
    -- Step 2: Insert default records
    
    INSERT INTO customers (customer_id, shop_id, email, first_name, last_name, state, verified_email, email_marketing_consent) VALUES
    (1, 1, 'customer1@example.com', 'John', 'Doe', 'CA', TRUE, '{"consent": true}'),
    (2, 2, 'customer2@example.com', 'Jane', 'Smith', 'NY', FALSE, '{"consent": false}');
    
    INSERT INTO shops (email) VALUES
    ('shop1@example.com'),
    ('shop2@example.com');
    
    INSERT INTO products (title, price) VALUES
    ('Product 1', 19.99),
    ('Product 2', 29.99);
    
    INSERT INTO webhooks_subscribed (webhook_topic) VALUES
    ('order_created'),
    ('customer_created');
    
    INSERT INTO integrators (name, config_file_path) VALUES
    ('MailChimp', 'sample_path'),
    ('MailXO', 'sample_path');
    
    INSERT INTO users (user_id, is_admin) VALUES
    ('user_001', TRUE),
    ('user_002', FALSE);
    
    INSERT INTO templates (name, description) VALUES
    ('Order Creation', 'Template for running workflow when order is created.');
    
    INSERT INTO templates_shop_mapping (template_id, shop_id) VALUES
    (1, 1),
    (1, 2);
    
    INSERT INTO automations (name, user_id, shop_id, webhook_id) VALUES
    ('Order Creation Workflow', 1, 1, 1);
    
    INSERT INTO nodes (node_type, auto_id) VALUES
    ('trigger', 1),
    ('condition', 1),
    ('delay', 1),
    ('integration', 1),
    ('http', 1);
    
    INSERT INTO edges (from_node_id, to_node_id) VALUES
    (1, 2),
    (2, 3),
    (2, NULL),
    (3, 4),
    (4, 5),
    (5, NULL);
    
    INSERT INTO fields (field_name, type) VALUES
    ('order_value', 'int');
    
    INSERT INTO nodes_fields_mapping (node_id, field_id) VALUES
    (2, 1);
    
    INSERT INTO condition_nodes (node_id, condition_type, sequence, operator, operand1, operand2) VALUES
    (2, 'if', 1, '>', 1, '10');
    
    INSERT INTO condition_node_mapping (node_id, eval, next_node_id) VALUES
    (2, TRUE, 3),
    (2, FALSE, NULL);
    
    INSERT INTO delay_nodes (node_id, delay_period) VALUES
    (1, 15);
    
    INSERT INTO integrator_nodes (node_id, integrator_id, context) VALUES
    (1, 1, '{"user_name": "user1"}');
    
    INSERT INTO http_nodes (node_id, http_method, http_url) VALUES
    (1, 'GET', 'https://example.com/api/get'),
    (2, 'POST', 'https://example.com/api/post');

    """)


def downgrade() -> None:
    pass
