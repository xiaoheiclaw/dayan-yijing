"""大衍筮法起卦 — 完整三变十八营流程"""

import secrets
from .hexagrams import lookup_hexagram, YAO_LINES, YAO_NAMES, is_changing
from .yao_ci import YAO_CI


def split_stalks(total: int) -> int:
    """分二：将蓍草随机分为左右两堆，返回左堆数量"""
    return secrets.randbelow(total - 1) + 1


def one_change(total: int) -> int:
    """一变：分二 → 挂一 → 揲四 → 归奇"""
    left = split_stalks(total)
    right = total - left

    # 挂一：右堆取出一根
    right -= 1
    guayi = 1

    # 揲四：左右各除4取余（余0按4算）
    left_remainder = left % 4 or 4
    right_remainder = right % 4 or 4

    removed = guayi + left_remainder + right_remainder
    return total - removed


def one_yao() -> int:
    """三变得一爻，返回 6(老阴) 7(少阳) 8(少阴) 9(老阳)"""
    stalks = 49

    stalks = one_change(stalks)   # 第一变：余 40 或 44
    stalks = one_change(stalks)   # 第二变
    stalks = one_change(stalks)   # 第三变

    # 最终蓍草数 ÷ 4 = 爻值
    return stalks // 4


def divine() -> list[int]:
    """十八变得六爻，自下而上"""
    return [one_yao() for _ in range(6)]


def format_result(yaos: list[int]) -> str:
    info = lookup_hexagram(yaos)
    lines = []

    lines.append(f"{'═' * 36}")
    lines.append(f"  {info['upper_symbol']} {info['upper']}({info['upper_nature']}) 上卦")
    lines.append(f"  {info['lower_symbol']} {info['lower']}({info['lower_nature']}) 下卦")
    lines.append(f"{'═' * 36}")
    lines.append(f"  第{info['seq']}卦 【{info['name']}】")
    lines.append(f"  {info['ci']}")
    lines.append(f"{'─' * 36}")

    # 自上而下画爻（第六爻在上）
    for i in range(5, -1, -1):
        yao = yaos[i]
        marker = " ←变" if is_changing(yao) else ""
        pos = YAO_NAMES[i]
        lines.append(f"  {pos}  {YAO_LINES[yao]}{marker}")

    changing = info.get("changing", [])
    if changing:
        lines.append(f"{'─' * 36}")
        pos_names = [YAO_NAMES[i] for i in changing]
        lines.append(f"  变爻：{', '.join(pos_names)}")

        yao_texts = YAO_CI.get(info["seq"], [])
        if yao_texts:
            lines.append(f"{'─' * 36}")
            lines.append(f"  【爻辞】")
            for i in changing:
                pos = YAO_NAMES[i]
                yx = "九" if yaos[i] == 9 else "六"
                if i == 0:
                    label = f"初{yx}"
                elif i == 5:
                    label = f"上{yx}"
                else:
                    label = f"{yx}{pos}"
                lines.append(f"  {label}：{yao_texts[i]}")

        lines.append(f"{'─' * 36}")
        zhi = info["zhi_gua"]
        lines.append(f"  之卦：第{zhi['seq']}卦 【{zhi['name']}】")
        lines.append(f"  {zhi['ci']}")
    else:
        lines.append(f"{'─' * 36}")
        lines.append(f"  无变爻（六爻皆静）")
        yao_texts = YAO_CI.get(info["seq"], [])
        if yao_texts:
            lines.append(f"  【卦辞主断】")

    lines.append(f"{'═' * 36}")
    return "\n".join(lines)


def main():
    print("\n  ── 大衍筮法 ──\n")
    yaos = divine()
    print(format_result(yaos))
    print()


if __name__ == "__main__":
    main()
