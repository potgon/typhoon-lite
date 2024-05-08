import tensorflow as tf
import json

from model_core.model_builders.model_base import ModelBase


class LSTMModel(ModelBase):
    def __init__(self, asset, units=50):
        super().__init__(asset)
        self.units = units

    def build_model(self):
        model = tf.keras.Sequential(
            [
                tf.keras.layers.LSTM(self.units, return_sequences=False),
                tf.keras.layers.Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        return model

    def to_dict(self):
        default_hyperparameters = {"units": self.units}
        description = """
        The Long Short-Term Memory (LSTM) model is a type of recurrent neural network (RNN)
        designed to capture long-term dependencies in sequential data.
        Unlike traditional RNNs, LSTM networks are equipped with memory cells that can maintain information over extended time intervals,
        allowing them to effectively learn and remember patterns in time series, text, and other sequential data
        """
        return {
            "model_name": "LSTM",
            "description": description,
            "default_hyperparameters": json.dumps(default_hyperparameters),
            "default_model_architecture": {
                "Layers": {"Layer1": "LSTM", "Layer2": "Dense(1)"}
            },
        }
