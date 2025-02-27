from __future__ import annotations
import sys
sys.path.append("./model")
import torch
import numpy as np
from typing import Generator
from io import BytesIO

from model.cosyvoice.cli.cosyvoice import CosyVoice2
from model.cosyvoice.utils.file_utils import load_wav

from ..utils.audio import wave_header_chunk, pack_audio

def load():
    return CosyVoice2('model_pretrained/CosyVoice2-0.5B', load_jit=False, load_trt=False, fp16=False)
cosyvoice: CosyVoice2 = load()

def stream_io(tts_text: Generator[str]):
    yield wave_header_chunk(sample_rate = cosyvoice.sample_rate)
    for text in tts_text:
        model_output = inference_zero_shot(text)
        for item in model_output:
            yield pack_audio(
                BytesIO(),
                (item["tts_speech"] * (2 ** 15)).numpy().astype(np.int16),
                cosyvoice.sample_rate,
                "raw"
            ).getvalue()

ModelOutput = Generator[dict[str, torch.Tensor], None, None]
def inference_zero_shot(tts_text: str) -> ModelOutput:
    return cosyvoice.inference_sft(
        tts_text, spk_id = "中文女",
        stream = True, text_frontend = False
    )

# 由于cosyvoice在初次运行的时候，会加载一些东西。为了避免这个延迟，启动时先自动跑一遍
for i in cosyvoice.inference_sft(
    "hi", spk_id = "中文女",
    stream = True, text_frontend = False
):
    continue
