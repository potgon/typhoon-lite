from typing import List, Dict
from fastapi import APIRouter, HTTPException, Depends

from database.models import ModelType, Asset, Queue, User
from api.schemas import ModelTypeModel
from utils.logger import make_log

router = APIRouter()


@router.get("/", response_model=List[ModelTypeModel])
async def read_all_models():
    model_queryset = await ModelType.all()
    if model_queryset is None:
        raise HTTPException(
            status_code=500, detail="Server error: model types could not be retrieved"
        )
    return model_queryset


@router.get("/{model_name}", response_model=ModelTypeModel)
async def read_model(model_name: str):
    model = await ModelType.filter(model_name=model_name).first()
    if model is None:
        raise HTTPException(status_code=404, detail="Model type not found")
    return model


@router.post("/enqueue")
async def enqueue_model(
    model_id: int, ticker: str, user_id: int
) -> Dict[str, str]:
    if not ticker or not model_id:
        raise HTTPException(status_code=400, detail="Missing ticker or model type id")

    asset = await Asset.filter(ticker=ticker).first()
    make_log("MODEL", 20, "api_workflow.log", f"Asset from request: {asset.ticker}")
    if asset is None:
        raise HTTPException(status_code=404, detail=f"Error retrieving ticker")

    model_type = await ModelType.filter(id=model_id).first()
    if model_type is None:
        raise HTTPException(status_code=404, detail=f"Error retrieving model_type")
    make_log("MODEL", 20, "api_workflow.log", f"Model from request: {model_type.id}")

    enqueued_model = await Queue.create(
        user=user_id, asset=asset, model_type=model_type
    )
    if not enqueued_model:
        raise HTTPException(
            status_code=500, detail="Server error: could not enqueue model"
        )
    return {"message": f"Model enqueued. ID: {enqueued_model.id}"}
