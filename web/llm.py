import json
import os
from collections.abc import AsyncGenerator

import anthropic

SYSTEM_PROMPT = """你是一位精通周易的卦师，有数十年研习易经的功底。你的解卦风格沉稳、通达，\
既尊重经典文本，又能结合问卦者的实际处境给出切实的指引。

解卦规则：
1. 先说明本卦的卦象大意（上下卦的象征及其组合含义）
2. 结合卦辞点明整体吉凶趋势
3. 若有变爻，逐一解读每条变爻爻辞，这是解卦的核心
4. 若有之卦（变卦），说明事态的演变方向
5. 最后综合所有信息，针对问卦者的具体问题给出明确建议
6. 若无变爻（六爻皆静），以卦辞为主断，着重解读整体卦义

风格要求：
- 使用现代中文，但可适当引用古文原文
- 语气如同面对面为人解卦，亲切而有分量
- 不要泛泛而谈，要给出具体的、可操作的建议
- 不要回避吉凶判断，该说凶就说凶，但要指出化解之道
- 篇幅适中，约 300-500 字
- 不要使用 markdown 格式标记"""

YAO_TYPE = {6: "老阴(变)", 7: "少阳", 8: "少阴", 9: "老阳(变)"}


def build_user_prompt(question: str, result: dict) -> str:
    h = result["hexagram"]
    yaos = result["yaos"]
    changing = result.get("changing", [])
    changing_ci = result.get("changing_yao_ci", [])
    zhi = result.get("zhi_gua")

    lines = [f"问卦者的问题：{question}", "", "--- 卦象 ---", ""]
    lines.append(f"本卦：第{h['seq']}卦 【{h['name']}】")
    lines.append(f"卦辞：{h['ci']}")
    lines.append(f"上卦：{h['upper']}({h['upper_nature']})  下卦：{h['lower']}({h['lower_nature']})")
    lines.append("")

    yao_names = ["初", "二", "三", "四", "五", "上"]
    lines.append("六爻（自下而上）：")
    for i, y in enumerate(yaos):
        lines.append(f"  {yao_names[i]}爻：{YAO_TYPE.get(y, str(y))}")
    lines.append("")

    if changing and changing_ci:
        lines.append("变爻及爻辞：")
        for ci in changing_ci:
            lines.append(f"  {ci['label']}：{ci['text']}")
        lines.append("")

    if zhi:
        lines.append(f"之卦：第{zhi['seq']}卦 【{zhi['name']}】")
        lines.append(f"卦辞：{zhi['ci']}")
    else:
        lines.append("六爻皆静，无变爻。以卦辞为主断。")

    lines.append("")
    lines.append("请为问卦者解读此卦。")
    return "\n".join(lines)


async def stream_interpretation(
    question: str, result: dict
) -> AsyncGenerator[str, None]:
    client = anthropic.AsyncAnthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    )
    user_prompt = build_user_prompt(question, result)

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0.7,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield json.dumps({"text": text}, ensure_ascii=False)
