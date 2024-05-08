from tortoise.exceptions import IncompleteInstanceError, IntegrityError

from database.models import Queue, FailedQueue
from model_core.trainer import Trainer
from model_core.failed_requests_trainer import FailedRequestsTrainer
from utils.logger import make_log


async def service_loop() -> None:
    trainer = Trainer()
    while True:
        try:
            trainer.train()
            make_log(
                "TRAINER_SERVICE",
                20,
                "trainer_service.log",
                f"Training current request...",
            )
        except TypeError as e:
            make_log(
                "TRAINER_SERVICE",
                40,
                "trainer_service.log",
                f"Failed at request: {trainer.current_request.id}. Trainer train method error: {str(e)}. Skipping request.",
            )
            manage_failed_request(trainer.current_request)
            continue
        trainer.evaluate()
        make_log(
            "TRAINER_SERVICE",
            20,
            "trainer_service.log",
            f"Performing evaluation metrics...",
        )
        model = trainer.save_model()
        make_log(
            "TRAINER_SERVICE",
            20,
            "trainer_service.log",
            f"Saving model to database...",
        )
        if model is None:
            make_log(
                "TRAINER_SERVICE",
                30,
                "trainer_service.log",
                "Error saving model, continuing with service...",
            )


async def check_failed_requests() -> None:
    make_log(
        "FAILED_REQUESTS_SERVICE",
        20,
        "trainer_service.log" "Initiating check on failed requests table...",
    )
    trainer = FailedRequestsTrainer()
    while True:
        queue_len = await FailedQueue.all().count()
        if queue_len == 0:
            make_log(
                "FAILED_REQUESTS_SERVICE", 30, "trainer_service.log"
                "Failed requests table is empty, stopping...", )
            break
        try:
            trainer.train()
            make_log(
                "FAILED_REQUESTS_SERVICE", 20, "trainer_service.log"
                "Re-training previously failed request...", )
        except TypeError as e:
            make_log(
                "FAILED_REQUESTS_SERVICE",
                40,
                "trainer_service.log",
                f"Failed at request: {trainer.current_request.id}. Trainer train method error: {str(e)}. Skipping request.",
            )
            manage_failed_request(trainer.current_request)
            continue
        trainer.evaluate()
        make_log(
            "FAILED_REQUESTS_SERVICE",
            20,
            "trainer_service.log" "Performing evaluation metrics...",
        )
        model = trainer.save_model()
        make_log(
            "FAILED_REQUESTS_SERVICE",
            20,
            "trainer_service.log"
            "Saving model...")
        if model is None:
            make_log(
                "FAILED_REQUESTS_SERVICE",
                30,
                "trainer_error.log",
                "Error saving model, continuing with service...",
            )
    make_log(
        "FAILED_REQUESTS_SERVICE",
        20,
        "trainer_service.log",
        "Failed requests checked, exiting service...",
    )


async def manage_failed_request(request: Queue) -> None:
    make_log(
        "TRAINER_SERVICE",
        20,
        "trainer_service.log",
        f"Managing failed request, REQUEST: {request.id}, {request.user_id}, {request.asset_id}, {request.model_type_id}",
    )
    try:
        await FailedQueue.save(
            asset_id=request.asset_id,
            model_type_id=request.model_type_id,
            user_id=request.user_id,
        )
    except (IncompleteInstanceError, IntegrityError) as e:
        make_log(
            "TRAINER_SERVICE",
            40,
            "trainer_service.log",
            f"Failed request could not be stored: {str(e)}",
        )
