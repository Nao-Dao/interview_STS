from __future__ import annotations
import sys
sys.path.append("./model")
import torch
import numpy as np
from typing import Generator
from io import BytesIO
from logging import getLogger
logger = getLogger(__name__)

from model.cosyvoice import CosyVoice2
from model.cosyvoice.utils.file_utils import load_wav

from core.utils.audio import wave_header_chunk, pack_audio

def load():
    return CosyVoice2('model_pretrained/CosyVoice2-0.5B', load_jit=False, load_trt=False, fp16=False)
cosyvoice: CosyVoice2 = load()

def stream_io(tts_text: Generator[str]):
    yield wave_header_chunk(sample_rate = cosyvoice.sample_rate)
    logger.debug("start generate tts")
    for text in tts_text:
        model_output = inference_instruct(text)
        for item in model_output:
            logger.debug("generate tts...")
            yield pack_audio(
                BytesIO(),
                (item["tts_speech"] * (2 ** 15)).numpy().astype(np.int16),
                cosyvoice.sample_rate,
                "raw"
            ).getvalue()

cosyvoice.frontend.generate_spk_info("spk", "上周，我去了一家意大利餐厅，它们的披萨简直太好吃了。", load_wav("model_pretrained/Xiaochen.wav", 16000))
ModelOutput = Generator[dict[str, torch.Tensor], None, None]
def inference_instruct(tts_text: str) -> ModelOutput:
    return cosyvoice.inference_instruct2_by_spk_id(
        tts_text, "在正式场合里讲话", "spk", 
        stream=True, text_frontend=False
    )
