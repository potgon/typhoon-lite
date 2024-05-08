from fastapi import APIRouter, HTTPException
from typing import List, Union, Dict
import yfinance as yf

from database.models import Asset
from api.schemas import AssetModel
from utils.logger import make_log

router = APIRouter()


@router.get("/", response_model=List[AssetModel])
async def read_all_assets():
    asset_queryset = await Asset.all()
    if asset_queryset is None:
        raise HTTPException(
            status_code=500,
            detail="Server error: assets could not be retrieved")
    return asset_queryset


@router.get("/{ticker}", response_model=AssetModel)
async def read_asset(ticker: str):
    asset = await Asset.filter(ticker=ticker).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("/bulk-add")
async def bulk_add(tickers: Union[str, List[str]]
                   ) -> Dict[str, Dict[str, str]]:
    if isinstance(tickers, str):
        tickers = [tickers]

    response = {}

    valid_assets = []
    for ticker in tickers:
        # try:
        data = yf.Ticker(ticker).info  # Not sure if this raises an exception
        # except Exception as e:
        #     make_log(
        #         "ASSETS",
        #         40,
        #         "api_error.log",
        #         f"Error fetching data for {ticker}: {str(e)}",
        #     )

        if data.get("shortName") is None:
            response[ticker] = "No data found. Ticker might be invalid"
            continue

        if await Asset.exists(ticker=ticker):
            response[ticker] = "Asset already in database"
            continue

        valid_assets.append(
            {
                "ticker": ticker,
                "name": data.get("shortName", None),
                "asset_type": data.get("quoteType", None),
                "sector": data.get("sector", None),
            }
        )

    if valid_assets:
        await Asset.bulk_create([Asset(**asset) for asset in valid_assets])
        for asset in valid_assets:
            if not await Asset.exists(ticker=asset["ticker"]):
                response[asset["ticker"]] = "Data could not be stored"
                continue
            response[asset["ticker"]] = "Data stored"

    return {"message": response}