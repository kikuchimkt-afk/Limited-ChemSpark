"""Targeted fixes for awkward "AはBはC" chains that were created when
the generic fix_tts pass replaced "A＝B＝C" with "AはBはC".

Each (file, old, new) pair is applied exactly once. old must occur
exactly once in the file to avoid accidental over-replacement.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).parent

FIXES: list[tuple[str, str, str]] = [
    # ch6-1
    (
        "ch6-1.json",
        "アミロースは直鎖状は長いらせんはヨウ素を多く取り込むは濃青色。アミロペクチンは枝分かれは短いらせんはヨウ素が少ないは赤紫色。",
        "アミロースは直鎖状で長いらせん構造をもち、ヨウ素を多く取り込むため濃青色。アミロペクチンは枝分かれ構造で短いらせんしか作れず、ヨウ素をあまり取り込まないため赤紫色。",
    ),
    (
        "ch6-1.json",
        "ヘミアセタールは開環できるはホルミル基が出現は還元性あり。アセタールは開環できないはホルミル基なしは還元性なし。",
        "ヘミアセタールは開環でき、ホルミル基が現れるため還元性あり。アセタールは開環できず、ホルミル基が現れないため還元性なし。",
    ),
    # ch6-2
    (
        "ch6-2.json",
        "シス形は折れ曲がり構造は柔軟はゴム弾性あり（天然ゴム）。トランス形は直線的構造は硬いは弾性なし（グッタペルカ）。",
        "シス形は折れ曲がり構造で柔軟、ゴム弾性あり（天然ゴム）。トランス形は直線的構造で硬く、弾性なし（グッタペルカ）。",
    ),
    # ch6-3
    (
        "ch6-3.json",
        "植物繊維はセルロースは多糖類。動物繊維はタンパク質。この分類は燃やしたときの臭いでも区別できます（タンパク質は焦げ臭いは毛を焼いた匂い）。",
        "植物繊維はセルロース、すなわち多糖類。動物繊維はタンパク質。この分類は燃やしたときの臭いでも区別できます（タンパク質は焦げ臭く、毛を焼いたような匂いがします）。",
    ),
    # ch5-5
    (
        "ch5-5.json",
        "セッケンは陰イオンは洗浄。逆性セッケンは陽イオンは殺菌。",
        "セッケンは陰イオン系で洗浄作用をもちます。逆性セッケンは陽イオン系で殺菌作用をもちます。",
    ),
    # ch5-4
    (
        "ch5-4.json",
        "フェノールはヒドロキシ基は弱酸性。アニリンはアミノ基は弱塩基性。",
        "フェノールはヒドロキシ基をもち弱酸性。アニリンはアミノ基をもち弱塩基性。",
    ),
    # ch5-3
    (
        "ch5-3.json",
        "「アルデヒドは還元性ありは銀鏡反応陽性。ケトンは還元性なしは銀鏡反応陰性」",
        "「アルデヒドは還元性ありで銀鏡反応陽性。ケトンは還元性なしで銀鏡反応陰性」",
    ),
    # ch5-2
    (
        "ch5-2.json",
        "エチレンは二重結合はアルケン、アセチレンは三重結合はアルキン。",
        "エチレンは二重結合をもつアルケン、アセチレンは三重結合をもつアルキン。",
    ),
    (
        "ch5-2.json",
        "アルカンは飽和は単結合は置換反応は臭素水脱色なし。アルケンは不飽和は二重結合は付加反応は臭素水脱色。アルキンは不飽和は三重結合は付加反応。",
        "アルカンは飽和の単結合のみで置換反応を起こし、臭素水を脱色しない。アルケンは不飽和で二重結合をもち、付加反応を起こして臭素水を脱色する。アルキンは不飽和で三重結合をもち、付加反応を起こす。",
    ),
    (
        "ch5-2.json",
        "アルカンは不飽和は付加反応。アルケンは飽和は置換反応。",
        "アルカンは不飽和で付加反応を起こす。アルケンは飽和で置換反応を起こす。",
    ),
    # ch5-1
    (
        "ch5-1.json",
        "水素の割合は二割る十八は約九分の一です。",
        "水素の割合は二割る十八、すなわち約九分の一です。",
    ),
    # ch4-4
    (
        "ch4-4.json",
        "トタンは亜鉛は屋外、ブリキはスズは食品。",
        "トタンは亜鉛めっきで屋外向け、ブリキはスズめっきで食品向け。",
    ),
    (
        "ch4-4.json",
        "黄銅は銅＋亜鉛は楽器。ジュラルミンはアルミ系は航空機。",
        "黄銅は銅と亜鉛の合金で楽器に使用。ジュラルミンはアルミニウム系の合金で航空機に使用。",
    ),
    (
        "ch4-4.json",
        "トタンは亜鉛は犠牲防食は屋外。ブリキはスズは被覆保護は食品。",
        "トタンは亜鉛めっきによる犠牲防食で屋外用。ブリキはスズめっきによる被覆保護で食品用。",
    ),
]


def apply_fix(path: Path, old: str, new: str) -> str:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        return f"  [SKIP] not found: {old[:40]}..."
    if count > 1:
        return f"  [WARN] {count}x matches for: {old[:40]}..."
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return f"  [OK]   fixed ({count}x match): {old[:40]}..."


def main() -> None:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for fname, old, new in FIXES:
        by_file.setdefault(fname, []).append((old, new))
    for fname, pairs in by_file.items():
        p = HERE / fname
        print(f"{fname}:")
        for old, new in pairs:
            print(apply_fix(p, old, new))


if __name__ == "__main__":
    main()
