import aiofiles
import json
import os
import tensorflow as tf
from keras.callbacks import History
from typing import Optional, ByteString

from model_core.model_builders.model_base import ModelBase
from model_core.model_utils.model_factory import ModelFactory
from database.models import TrainedModel, ModelType, Queue
from utils.logger import make_log


class Trainer:
    def __init__(self):
        self.val_performance = {}
        self.performance = {}
        self.current_request: Queue = None  # Queue Instance
        self.priority_counter = 0
        self.current_model_instance: ModelBase = None  # Model Builder Instance
        self.current_trained_model = None  # Keras Model

    async def _get_next_queue_item(self) -> Optional[Queue]:
        """Uses self.priority_counter to retrieve the next priority or non-priority item from the queue

        Returns:
            Optional[Queue]: Queue instance
        """

        queue_item = (
            await Queue.filter(priority=1 if self.priority_counter < 5 else 0)
            .order_by("created_at")
            .first()
        )

        if queue_item:
            self._manage_prio_counter(queue_item.priority)
            make_log(
                "TRAINER",
                20,
                "trainer_workflow.log",
                f"Queue item correctly fetched: {queue_item.id}",
            )
            return queue_item
        else:
            make_log(
                "TRAINER",
                30,
                "trainer_workflow.log",
                f"No queue item found: {queue_item}",
            )
            return None

    def _manage_prio_counter(self, queue_item_priority: int) -> None:
        """Keeps track of completed priority requests and manages self.priority_counter

        Args:
            queue_item_priority (int): Queue item instance priority field
        """
        if queue_item_priority == 1:
            self.priority_counter += 1
        else:
            self.priority_counter = 0
        make_log(
            "TRAINER",
            20,
            "trainer_workflow.log",
            f"Queue priority counter adjusted: {self.priority_counter}",
        )

    def _compile_and_fit(
            self,
            model,
            window,
            epochs=20,
            patience=2) -> History:
        """Compiles and fits current model instance to given data window

        Args:
            model (ModelBase): Model builder instance
            window (WindowGenerator): Data window
            epochs (int, optional): _description_. Defaults to 20.
            patience (int, optional): _description_. Defaults to 2.

        Returns:
            History: Keras History object, records events
        """
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=patience, mode="min"
        )
        model.compile(
            loss=tf.losses.MeanSquaredError(),
            optimizer=tf.optimizers.Adam(),
            metrics=[tf.metrics.MeanAbsoluteError()],
        )
        history = model.fit(
            window.train,
            epochs=epochs,
            validation_data=window.val,
            callbacks=[early_stopping],
        )
        make_log(
            "TRAINER",
            20,
            "trainer_workflow.log",
            "Model compiled and fit")

        return history

    async def train(self) -> None:
        """Gets model type and asset from current request and trains it

        Raises:
            TypeError: Raised if no queue item could be retrieved
            TypeError: Raised if factory could not return any model instance
        """
        self.current_request = self._get_next_queue_item()
        if self.current_request is None:
            queue_error = "Cannot retrieve queue item"
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                queue_error,
            )
            raise TypeError(queue_error)  # Caught in service module
        built_model = ModelFactory.get_built_model(
            self.current_request.model_type, self.current_request.asset
        )
        if not built_model:
            model_error = "Could not retrieve model instance from model factory"
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                model_error,
            )
            raise TypeError(model_error)  # Caught in service module
        self.current_model_instance = built_model
        self.current_trained_model = self._compile_and_fit(
            self.current_model_instance.model, self.current_model_instance.window)
        make_log(
            "TRAINER",
            20,
            "trainer_workflow.log",
            "Model successfully built")

    def evaluate(self) -> None:
        """Stores performance metrics of current trained model"""
        self.val_performance = self.current_trained_model.evaluate(
            self.current_model_instance.window.val
        )
        self.performance = self.current_trained_model.evaluate(
            self.current_model_instance.window.test, verbose=0
        )
        make_log(
            "TRAINER",
            20,
            "trainer_workflow.log",
            "Model evaluation successful")

    async def save_model(self) -> Optional[TrainedModel]:
        """Saves current trained model to database

        Returns:
            Optional[TrainedModel]: TrainedModel instance
        """
        model_dict = self.current_model_instance.to_dict()
        self._save_new_model_type(model_dict)
        serialized_model = self._serialize_model()

        model = await TrainedModel.create(
            model_type=self.current_model_instance,
            asset=self.current_request.asset,
            user=self.current_request.user,
            model_name=model_dict["model_name"],
            performance_metrics=json.dumps(self.performance),
            hyperparameters=model_dict["default_hyperparameters"],
            model_architecture=model_dict["default_model_architecture"],
            serialized_model=serialized_model,
            training_logs=json.dumps(self.val_performance),
            status="Temporal",
        )
        if model is None:
            make_log(
                "TRAINER",
                40,
                "trainer_workflow.log",
                f"Error saving model",
            )
            return None
        make_log(
            "TRAINER",
            20,
            "trainer_workflow.log",
            "Model successfully saved")
        return model

    # async def save_temp_model(self) -> Optional[TempModel]:
    #     model_dict = self.current_model_instance.to_dict()
    #     serialized_model = self._serialize_model()
    #     try:
    #         model = await TempModel.create(
    #             model_type = self.current_model_instance,
    #             asset = self.current_request.asset,
    #             user = self.current_request.user,
    #             model_name=model_dict["model_name"],
    #             performance_metrics=json.dumps(self.performance),
    #             hyperparameters=model_dict["default_hyperparameters"],
    #             model_architecture=model_dict["default_model_architecture"],
    #             serialized_model=serialized_model,
    #             training_logs=json.dumps(self.val_performance),
    #             status="Temporal",
    #         )
    #     except BaseORMException as e:
    #         make_log(
    #             "TRAINER",
    #             40,
    #             "trainer_workflow.log",
    #             f"Error saving temporal model: {str(e)}",
    #         )
    #         return None
    #     return model

    async def _serialize_model(self) -> ByteString:
        """Serializes current trained model

        Returns:
            ByteString: ByteString containing Binary serialized model
        """
        save_path = os.getenv("TRAINED_MODEL_SAVE_PATH")
        self.current_trained_model.save(save_path)
        async with aiofiles.open(save_path, "rb") as file:
            serialized_model = await file.read()
        os.remove(save_path)
        make_log(
            "TRAINER",
            20,
            "trainer_workflow.log",
            "Model successfully serialized")
        return serialized_model

    async def _save_new_model_type(self, model_dict) -> None:
        """Checks if model type of current trained model does not exist and creates it otherwise

        Args:
            model_dict (Dict): Dict with model instance info sent from save_temp_model

        Returns:
            None
        """
        model_type_exists = await ModelType.filter(
            model_name=model_dict["model_name"]
        ).exists()

        if not model_type_exists:
            new_model = await ModelType.create(
                name=model_dict["model_name"],
                description=model_dict["description"],
                default_hyperparameters=model_dict["default_hyperparameters"],
                default_model_architecture=model_dict["default_model_architecture"],
            )
            make_log(
                "TRAINER",
                20,
                "trainer_workflow.log",
                f"New model type stored: Is ModelType = {new_model} ?",
            )
        else:
            make_log(
                "TRAINER",
                20,
                "trainer_workflow.log",
                f"Nothing created. Is True  = {model_type_exists} ?",
            )
