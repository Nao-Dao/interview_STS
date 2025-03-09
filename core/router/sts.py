from  __future__ import annotations
import fastapi
from typing import Annotated, List
from .utils import stream_text_to_speech, generate_msg, put_llm, save_audio

router = fastapi.APIRouter()
@router.get("/api/tts")
async def tts(cid: int):
    return fastapi.responses.StreamingResponse(stream_text_to_speech(cid), media_type="audio/wav")

from model.sensor import asr as sensor
from ..utils.audio import webm2wav
@router.post("/api/asr")
async def asr(files: Annotated[List[bytes], fastapi.File(description="wav or mp3 audios in 16KHz")],
              lang: Annotated[str, fastapi.Form(description="language of audio content")] = "auto",
              cid: Annotated[int, fastapi.Form()] = None):
    b = webm2wav(files[0])
    resp = sensor(b, lang)
    if len(resp.text):
        put_llm(resp.text, cid)
        save_audio(cid, b)
    return fastapi.responses.JSONResponse({})

from ..utils.snowflake import generate_snowflake_id
@router.get("/api/id")
async def get_id():
    return fastapi.Response(str(generate_snowflake_id()))
