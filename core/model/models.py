from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import relationship

Base = declarative_base()

# Enums
data_type = ENUM('int', 'string', 'datetime', name='data_type', create_type=False)
comparison_operator = ENUM('=', '<', '>', '<=', '>=', name='comparison_operator', create_type=False)
condition_type = ENUM('if', 'switch', 'if-elseif', name='condition_type', create_type=False)
node_type = ENUM('condition', 'action', 'trigger', 'http', 'delay', 'integration', name='node_type', create_type=False)
execution_state = ENUM('NEW', 'IN_PROGRESS', 'PAUSE', 'COMPLETE', 'RETRY', name='execution_state', create_type=False)
status = ENUM('FAILED', 'SUCCESS', 'RUNNING', name='status', create_type=False)


# Models
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    shop_id = Column(Integer, nullable=False)
    email = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    state = Column(String(50))
    verified_email = Column(Boolean)
    email_marketing_consent = Column(JSONB)


class Shop(Base):
    __tablename__ = 'shops'
    shop_id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    shop_id = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=False)
    payload = Column(JSONB)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)


class WebhookSubscribed(Base):
    __tablename__ = 'webhooks_subscribed'
    id = Column(Integer, primary_key=True)
    webhook_topic = Column(String(255), nullable=False)


class Integrator(Base):
    __tablename__ = 'integrators'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    config_file_path = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    is_admin = Column(Boolean)


class Template(Base):
    __tablename__ = 'templates'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String)


class TemplateShopMapping(Base):
    __tablename__ = 'templates_shop_mapping'
    template_id = Column(Integer, ForeignKey('templates.id'), primary_key=True)
    shop_id = Column(Integer, ForeignKey('shops.shop_id'), primary_key=True)


class Automation(Base):
    __tablename__ = 'automations'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shop_id = Column(Integer, ForeignKey('shops.shop_id'), nullable=False)
    webhook_id = Column(Integer, nullable=False)


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    node_type = Column(node_type, nullable=False)
    auto_id = Column(Integer, ForeignKey('automations.id'), nullable=False)
    edges = relationship('Edge', lazy='joined')
    from_edges = relationship('Edge', foreign_keys='Edge.from_node_id', back_populates='from_node')
    to_edges = relationship('Edge', foreign_keys='Edge.to_node_id', back_populates='to_node')


class Edge(Base):
    __tablename__ = 'edges'
    from_node_id = Column(Integer, ForeignKey('nodes.id'))
    to_node_id = Column(Integer, ForeignKey('nodes.id'))
    from_node = relationship('Node', foreign_keys=[from_node_id], back_populates='from_edges')
    to_node = relationship('Node', foreign_keys=[to_node_id], back_populates='to_edges')


class Field(Base):
    __tablename__ = 'fields'
    id = Column(Integer, primary_key=True)
    field_name = Column(String(255), nullable=False)
    type = Column(data_type, nullable=False)


class NodeFieldMapping(Base):
    __tablename__ = 'nodes_fields_mapping'
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    field_id = Column(Integer, ForeignKey('fields.id'), primary_key=True)


class ConditionNode(Base):
    __tablename__ = 'condition_nodes'
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    condition_type = Column(condition_type, nullable=False)
    sequence = Column(Integer, nullable=False)
    operator = Column(comparison_operator, nullable=False)
    operand1 = Column(Integer, ForeignKey('fields.id'), nullable=False)
    operand2 = Column(String(255))


class ConditionNodeMapping(Base):
    __tablename__ = 'condition_node_mapping'
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    eval = Column(Boolean, nullable=False)
    next_node_id = Column(Integer, ForeignKey('nodes.id'))


class DelayNode(Base):
    __tablename__ = 'delay_nodes'
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    delay_period = Column(Integer, nullable=False)


class IntegratorNode(Base):
    __tablename__ = 'integrator_nodes'
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    integrator_id = Column(Integer, ForeignKey('integrators.id'), nullable=False)
    context = Column(JSONB)


class HttpNode(Base):
    __tablename__ = 'http_nodes'
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    http_method = Column(String(10), nullable=False)
    http_url = Column(String(255), nullable=False)


class WorkflowExecution(Base):
    __tablename__ = 'workflow_execution'
    id = Column(Integer, primary_key=True)
    state = Column(execution_state, nullable=False)
    curr_node_id = Column(Integer, ForeignKey('nodes.id'), nullable=False)
    auto_id = Column(Integer, nullable=False)
    retry = Column(Boolean)
    status = Column(status, nullable=False)
    start_time = Column(TIMESTAMP, default='NOW()')
    update_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)


class NodeExecution(Base):
    __tablename__ = 'node_execution'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=False)
    next_node_id = Column(Integer, ForeignKey('nodes.id'))
    workflow_id = Column(Integer, ForeignKey('workflow_execution.id'), nullable=False)
    state = Column(execution_state, nullable=False)
    start_time = Column(TIMESTAMP, default='NOW()')
    end_time = Column(TIMESTAMP)
    retry = Column(Boolean)
