from core.repository.db import get_db
from core.repository.workflow_repository import get_automation_repository


def load_workflow(webhook_data):
    """
    1. query the automations table and load the workflow object
    2. from that automation_id, load the nodes and edges
    3. once loaded parse nodes into a graph and send to executor
        :param webhook_data:
        :return:
    """
    db = next(get_db())
    automation = load_automation(db, webhook_data)
    return automation


def load_automation(db, webhook_data):
    repo = get_automation_repository(db)
    webhook_id = webhook_data.id
    shop_id = webhook_id.shop_id
    automation = repo.get_automation_by_webhook_shop(webhook_id, shop_id)
    return automation
