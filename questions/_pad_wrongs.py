"""Pad the wrong-answer text of specific length-biased questions in ch1-1.json
so that correct choices no longer stand out by length alone.

Identifies each target by (question_id, original TTS text of the wrong choice)
to be robust against the prior shuffle step. Updates both ``tts_text`` and
``text`` (they are equal for these rewrites because the new wrong texts
contain no kanji numerals, unit words, compound-formula names, or 選択肢○
references).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path(__file__).parent / "ch1-1.json"

# (qid, original_tts_text_to_match) -> new_tts_text
REPLACEMENTS: dict[tuple[str, str], str] = {
    # ---------------- q006 ろ過の定義 (correct 46ch) ----------------
    (
        "ch1_1_q006",
        "液体に溶けている固体を、ろ紙を用いて分離する操作である。",
    ): "液体に溶けて均一な溶液になっている固体を、ろ紙の目を用いて液体から直接取り除く操作である。",
    (
        "ch1_1_q006",
        "沸点の異なる液体の混合物を加熱して分離する操作である。",
    ): "沸点の異なる液体の混合物を加熱し、蒸発と冷却を繰り返して成分を分離・精製する操作である。",
    (
        "ch1_1_q006",
        "融点の差を利用して固体同士の混合物を分離する操作である。",
    ): "融点の差を利用して、固体同士の混合物を加熱し、溶け出した順に取り分けて分離する操作である。",

    # ---------------- q034 蒸留の温度計位置 (correct 29ch) ----------------
    (
        "ch1_1_q034",
        "液体の温度を正確に測るためである。",
    ): "フラスコ内の液体の温度を直接測定して沸騰状態を判定するためである。",
    (
        "ch1_1_q034",
        "沸騰石が飛び散るのを見張るためである。",
    ): "沸騰石が飛び散るのを観察しやすい位置で監視するためである。",
    (
        "ch1_1_q034",
        "フラスコが破損するのを防ぐためである。",
    ): "加熱による温度上昇でフラスコが急激に膨張し破損するのを防ぐためである。",

    # ---------------- q037 同素体と同位体 (correct 57ch) ----------------
    (
        "ch1_1_q037",
        "同素体と同位体はどちらも原子の中性子の数が異なるために区別される。",
    ): "同素体も同位体もどちらも原子核中の中性子の数が異なることによって区別される同じ概念である。",
    (
        "ch1_1_q037",
        "同素体は原子の種類の違い、同位体は物質の性質の違いである。",
    ): "同素体は中性子数による原子の種類の違いであり、同位体は原子の配列による物質の性質の違いである。",
    (
        "ch1_1_q037",
        "どちらも異なる元素どうしの関係を指す。",
    ): "どちらも元素の種類そのものが異なる物質や原子どうしの関係を指し、同じ元素内では成立しない。",

    # ---------------- q039 化合物と混合物 (correct 44ch) ----------------
    (
        "ch1_1_q039",
        "混合物は化学的な結合で結びついた純物質である。",
    ): "混合物は複数の物質が化学的な結合で強く結びついた純物質であり、組成比が常に一定である。",
    (
        "ch1_1_q039",
        "化合物は物理的な方法で容易に構成元素に分解できる。",
    ): "化合物はろ過や蒸留などの物理的な方法で容易に構成元素そのものへ分解できる純物質である。",
    (
        "ch1_1_q039",
        "化合物も混合物も純物質であり、融点や沸点は常に一定である。",
    ): "化合物も混合物も同じ純物質の仲間であり、融点や沸点は濃度によらず常に一定の値を示す。",

    # ---------------- q049 蒸留総合 (correct 66ch) ----------------
    (
        "ch1_1_q049",
        "液量を半分以下は冷却効率、沸騰石は気体温度測定、温度計の位置は突沸防止、冷却水の向きは液体温度測定のためである。",
    ): "液量を半分以下は冷却効率の向上、沸騰石は気体温度の測定、温度計の位置は突沸防止、冷却水の向きは液体温度の正確な測定のためである。",
    (
        "ch1_1_q049",
        "すべての操作はフラスコの破損を防ぐためのもので、分離精度には関係がない。",
    ): "すべての操作はフラスコや冷却器の破損を熱衝撃から防ぐための安全措置であり、分離精度とは無関係である。",
    (
        "ch1_1_q049",
        "すべての操作は単に加熱を促進するために行われる。",
    ): "すべての操作は加熱効率を高めて加熱時間をできる限り短縮し、素早く留出液を得るための工夫である。",

    # ---------------- q050 総合 (correct 109ch) ----------------
    (
        "ch1_1_q050",
        "同素体と同位体はどちらも混合物の一種であり、アボガドロの法則は液体の体積に関する法則、質量保存の法則は気体にのみ成立する。",
    ): "同素体と同位体はどちらも均一混合物の一種で純物質ではなく、アボガドロの法則は液体の体積と圧力の関係を表し、質量保存の法則は気体の化学変化にのみ成立して固体や液体では成り立たない法則である。",
    (
        "ch1_1_q050",
        "同素体は中性子数の違いによる原子の種類、同位体は原子配列の違いによる物質の種類、アボガドロは質量保存の法則を提唱、ラボアジエは分子説を提唱した。",
    ): "同素体は中性子数の違いによる原子の種類で、同位体は原子配列の違いによる物質の種類の名称、アボガドロは質量保存の法則をフランスで提唱した研究者、ラボアジエは分子説を提唱して気体反応の矛盾を解決した化学者である。",
    (
        "ch1_1_q050",
        "同素体と同位体は同じ意味で、アボガドロはゲーリュサックの法則を否定し、質量保存の法則は化学変化では成立しない。",
    ): "同素体と同位体は完全に同じ意味の言葉であって区別の必要はなく、アボガドロはゲーリュサックの気体反応の法則を否定して原子説を新たに提唱し、質量保存の法則は化学変化の前後では成立せず物理変化にのみ適用される。",
}


def main() -> int:
    with P.open(encoding="utf-8") as f:
        data = json.load(f)

    applied = 0
    unmatched: list[tuple[str, str]] = []
    for (qid, old_tts), new_tts in REPLACEMENTS.items():
        q = next((x for x in data["questions"] if x["id"] == qid), None)
        if q is None:
            unmatched.append((qid, old_tts))
            continue
        target = None
        for c in q["choices"]:
            if c.get("tts_text") == old_tts:
                target = c
                break
        if target is None:
            unmatched.append((qid, old_tts))
            continue
        target["tts_text"] = new_tts
        # None of the padded wrongs contain numbers/units/formulas/choice-refs,
        # so display form is identical to TTS form.
        target["text"] = new_tts
        applied += 1

    if unmatched:
        print("UNMATCHED (review required):")
        for qid, t in unmatched:
            print(f"  - {qid}: {t!r}")

    with P.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"applied {applied} replacements / total {len(REPLACEMENTS)}")

    # re-run length diagnostic
    from collections import Counter
    qs = data["questions"]
    pos = Counter()
    longest_is_correct = 0
    correct_len_total = 0
    wrong_len_total = 0
    wrong_count = 0
    flagged = []
    for q in qs:
        choices = q["choices"]
        for i, c in enumerate(choices):
            if c.get("is_correct"):
                pos[i + 1] += 1
                cl = len(c["text"])
                correct_len_total += cl
                lens = [len(cc["text"]) for cc in choices]
                if cl == max(lens):
                    longest_is_correct += 1
            else:
                wrong_len_total += len(c["text"])
                wrong_count += 1
        correct = next(c for c in choices if c["is_correct"])
        wrongs = [c for c in choices if not c["is_correct"]]
        cl = len(correct["text"])
        max_wl = max(len(c["text"]) for c in wrongs)
        if cl > max_wl and cl - max_wl >= 10:
            flagged.append((q["id"], cl, max_wl, cl - max_wl))

    print(f"\nCorrect positions: {dict(sorted(pos.items()))}")
    print(
        f"Longest-is-correct: {longest_is_correct}/{len(qs)} "
        f"({longest_is_correct/len(qs)*100:.0f}%)"
    )
    print(f"Avg correct length: {correct_len_total/len(qs):.1f}")
    print(f"Avg wrong length:   {wrong_len_total/wrong_count:.1f}")
    print(f"Remaining length-biased (diff>=10): {len(flagged)}")
    for qid, cl, wl, diff in flagged:
        print(f"  {qid}: correct={cl} max_wrong={wl} diff=+{diff}")

    return 0 if not unmatched else 1


if __name__ == "__main__":
    raise SystemExit(main())
