from typing import Optional
from tortoise.exceptions import MultipleObjectsReturned, DoesNotExist

from model_core.model_builders.model_base import ModelBase
from database.models import FailedQueue
from model_core.trainer import Trainer
from utils.logger import make_log


class FailedRequestsTrainer(Trainer):
    def __init__(self):
        self.val_performance = {}
        self.performance = {}
        self.current_request: FailedQueue = None  # Failed requests Queue Instance
        self.current_model_instance: ModelBase = None  # Model Builder Instance
        self.current_trained_model = None  # Keras Model

    async def _get_next_queue_item(
        self
    ) -> Optional[FailedQueue]:
        try:
            queue_len = await FailedQueue.all().count()
            if queue_len == 0:
                return None
            queue_item = await FailedQueue.get()
        except (MultipleObjectsReturned, DoesNotExist) as e:
            make_log(
                "FAILED_REQUESTS_TRAINER",
                30,
                "trainer_workflow.log",
                f"Error retrieving queue item: {str(e)}. \n Is Queue empty? {queue_len}")

        if queue_item:
            make_log(
                "FAILED_REQUESTS_TRAINER",
                20,
                "trainer_workflow.log",
                f"Queue item correctly fetched: {queue_item.id}",
            )
            return queue_item
        else:
            make_log(
                "FAILED_REQUESTS_TRAINER",
                30,
                "trainer_workflow.log",
                f"No queue item found: {queue_item}",
            )
            return None
