import asyncio
import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models.translation.indictrans import get_translator

router = APIRouter()


class SummaryTranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1200)
    language: Literal["kn", "hi", "pa", "gu", "mr", "te", "ta"]


@router.post("/translate")
async def translate_summary(payload: SummaryTranslationRequest) -> dict[str, str]:
    try:
        translator = await asyncio.to_thread(get_translator)
        translated_text = await asyncio.to_thread(
            translator.translate,
            payload.text,
            payload.language,
        )
    except Exception as exc:
        logging.exception("Local farmer-summary translation failed.")
        raise HTTPException(
            status_code=503,
            detail="Local translation is unavailable. Check API logs and model setup.",
        ) from exc

    return {"language": payload.language, "translated_text": translated_text}
