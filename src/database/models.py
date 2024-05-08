from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    password = fields.CharField(max_length=128)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=50, unique=True)
    date_joined = fields.DatetimeField(auto_now_add=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    priority = fields.BooleanField(default=False)
    tokens = fields.IntField(default=0)

    def __str__(self):
        return f"{self.email}"


class Asset(Model):
    id = fields.IntField(pk=True)
    ticker = fields.CharField(max_length=20, unique=True)
    name = fields.CharField(max_length=50)
    sector = fields.CharField(max_length=50, null=True)
    asset_type = fields.CharField(max_length=50, null=True)


class ModelType(Model):
    id = fields.IntField(pk=True)
    model_name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField()
    default_hyperparameters = fields.JSONField()
    default_model_architecture = fields.JSONField()

    def __str__(self):
        return self.model_name


class TrainedModel(Model):
    id = fields.IntField(pk=True)
    model_type = fields.ForeignKeyField(
        "models.ModelType", null=True, on_delete=fields.CASCADE
    )
    user = fields.ForeignKeyField("models.User", null=True, on_delete=fields.CASCADE)
    asset = fields.ForeignKeyField("models.Asset", null=True, on_delete=fields.CASCADE)
    model_name = fields.CharField(max_length=50)
    training_timestamp = fields.DatetimeField(auto_now_add=True)
    performance_metrics = fields.JSONField()
    hyperparameters = fields.JSONField()
    model_architecture = fields.JSONField()
    serialized_model = fields.BinaryField()
    training_performance = fields.JSONField()
    status = fields.CharField(max_length=25, default="Inactive")

    def __str__(self):
        return self.model_name


class TempModel(Model):
    id = fields.IntField(pk=True)
    model_type = fields.ForeignKeyField(
        "models.ModelType", null=True, on_delete=fields.CASCADE
    )
    user = fields.ForeignKeyField("models.User", null=True, on_delete=fields.CASCADE)
    asset = fields.ForeignKeyField("models.Asset", null=True, on_delete=fields.CASCADE)
    model_name = fields.CharField(max_length=50)
    training_timestamp = fields.DatetimeField(auto_now_add=True)
    performance_metrics = fields.JSONField()
    hyperparameters = fields.JSONField()
    model_architecture = fields.JSONField()
    serialized_model = fields.BinaryField()
    training_performance = fields.JSONField()
    status = fields.CharField(max_length=25, default="Temporal")

    def __str__(self):
        return self.model_name


class Queue(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    asset = fields.ForeignKeyField("models.Asset", on_delete=fields.CASCADE)
    model_type = fields.ForeignKeyField("models.ModelType", on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)
    priority = fields.BooleanField(default=False)

    class Meta:
        ordering = ["priority", "created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.asset.name} - {self.model_type.model_name}"


class FailedQueue(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    asset = fields.ForeignKeyField("models.Asset", on_delete=fields.CASCADE)
    model_type = fields.ForeignKeyField("models.ModelType", on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.asset.name} - {self.model_type.model_name}"
