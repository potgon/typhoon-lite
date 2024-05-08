import os
from typing import Optional, Dict, Type

from model_core.model_builders.model_base import ModelBase
from model_core.model_builders.lstm_model import LSTMModel
from database.models import ModelType
from utils.logger import make_log

MODEL_MAPPING = Dict[str, Type[ModelBase]] = {
    os.getenv("LSTM_MODEL_NAME"): LSTMModel,
}


class ModelFactory:
    @staticmethod
    async def get_built_model(
            model_type_id: int,
            **kwargs) -> Optional[ModelBase]:
        model_type = await ModelType.filter(id=model_type_id).first()

        if not model_type:
            make_log(
                "MODEL_FACTORY",
                40,
                "trainer_workflow.log",
                "No model type found")
            return None

        model_constructor = MODEL_MAPPING.get(model_type.model_name, None)
        if model_constructor:
            try:
                model_constructor(**kwargs)
                return model_constructor(**kwargs)
            except TypeError:
                return None

        make_log(
            "MODEL_FACTORY",
            40,
            "trainer_workflow.log",
            f"No model constructor found for model type: {model_type.model_name}",
        )
