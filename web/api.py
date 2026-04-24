from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.dayan import divine
from src.hexagrams import (
    lookup_hexagram, YAO_NAMES, TRIGRAM_SYMBOLS, TRIGRAM_NATURE,
    is_changing,
)
from src.yao_ci import YAO_CI
from .llm import stream_interpretation

router = APIRouter(prefix="/api")


class DivineRequest(BaseModel):
    question: str = ""


class InterpretRequest(BaseModel):
    question: str
    result: dict


def _yao_label(index: int, yao_value: int) -> str:
    yx = "九" if yao_value in (7, 9) else "六"
    if index == 0:
        return f"初{yx}"
    if index == 5:
        return f"上{yx}"
    return f"{yx}{YAO_NAMES[index]}"


@router.post("/divine")
async def api_divine(req: DivineRequest):
    yaos = divine()
    info = lookup_hexagram(yaos)
    yao_texts = YAO_CI.get(info["seq"], [])

    changing_yao_ci = []
    for i in info["changing"]:
        changing_yao_ci.append({
            "position": YAO_NAMES[i],
            "label": _yao_label(i, yaos[i]),
            "text": yao_texts[i] if i < len(yao_texts) else "",
        })

    result = {
        "yaos": yaos,
        "hexagram": {
            "seq": info["seq"],
            "name": info["name"],
            "ci": info["ci"],
            "upper": info["upper"],
            "lower": info["lower"],
            "upper_symbol": info["upper_symbol"],
            "lower_symbol": info["lower_symbol"],
            "upper_nature": info["upper_nature"],
            "lower_nature": info["lower_nature"],
        },
        "changing": info["changing"],
        "changing_yao_ci": changing_yao_ci,
    }

    if "zhi_gua" in info:
        zhi = info["zhi_gua"]
        result["zhi_gua"] = {
            "seq": zhi["seq"],
            "name": zhi["name"],
            "ci": zhi["ci"],
        }

    return result


@router.post("/interpret")
async def api_interpret(req: InterpretRequest):
    async def event_stream():
        async for chunk in stream_interpretation(req.question, req.result):
            yield f"data: {chunk}\n\n"
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
