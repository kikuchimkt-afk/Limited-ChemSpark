# 節ごとの詳細検証手順

本ドキュメントは、各節（chapter）のクイズデータに対して **手動で品質検証を行い、
問題を修正する** ための再現可能な手順を定めたものである。

`WORKFLOW.md` の自動バリデーション（`_check_all.py`）では検出できない
**内容・教育品質の問題** を対象とする。

---

## 前提条件

- `python questions\_check_all.py <chapter>` が **ALL CHECKS PASSED** であること
- 自動チェックをパスしていても、以下の手動検証は必須

---

## Phase 1：全問精読（検出）

### 1.1 チェック観点

全問に対し、以下の5観点で精読する。

| # | 観点 | 確認内容 |
|---|------|---------|
| 1 | **答え漏洩** | 誤答選択肢のテキストに正解情報が含まれていないか（「逆でXが正しい」「正しい記述であり」等） |
| 2 | **文の完結性** | 選択肢テキストが「だが、」「誤りで、」等で途中終了していないか |
| 3 | **科学的正確性** | 正解選択肢の内容が科学的に正しいか。誤答が「ありえない」レベルではなく教育的トラップになっているか |
| 4 | **trap_detail の品質** | 各選択肢の `trap_detail` が「この記述は正しい。」だけで終わっていないか。なぜ正しい／なぜ誤りかの具体的説明があるか |
| 5 | **TTS制約** | `tts_*` フィールドに化学式・記号・数式・`選択肢N` が含まれていないか |

### 1.2 チェック用コマンド

```powershell
# 全問のテキストを一覧表示（読み取り専用）
python _tmp\extract_pad_targets.py          # 長さバイアスの全体像
python questions\_check_all.py <chapter>     # 自動チェック（前提確認）
```

### 1.3 問題の記録

検出した問題をカテゴリ別に記録する。

| カテゴリ | 深刻度 | 説明 |
|---------|--------|------|
| **A: 答え漏洩** | 🔴 致命的 | 誤答選択肢内で正解を暴露 |
| **B: 文截れ** | 🟠 重大 | テキストが途中で終わっている（音声も途中終了） |
| **C: 科学的誤り** | 🔴 致命的 | 正解が科学的に間違っている |
| **D: trap_detail不足** | 🟡 中程度 | 解説が不十分 |
| **E: TTS違反** | 🟠 重大 | `_validate.py` で検出されるべきだが漏れているもの |

---

## Phase 2：答え漏洩の修正

### 2.1 修正スクリプト

`questions/_fix_answer_leak.py` を使用する。このスクリプトは以下の2パターンを
ヒューリスティックで自動修正する。

| パターン | 対象 | 修正方法 |
|---------|------|---------|
| `question_type: "correct"` の誤答 | 「Wrong claim. 逆でCorrect.」 | 最初の文（誤りの主張）だけを残す |
| `question_type: "incorrect"` の正答 | 「Fact. これは正しい記述であり…」 | 自己ラベル部分を除去 |

### 2.2 手動オーバーライド

ヒューリスティックで処理できない複雑なケース（文中に「が、逆で」が埋め込まれて
いる等）は、スクリプト内の `OVERRIDES` 辞書に `choice_id → 修正テキスト` を
追加する。

### 2.3 実行手順

```powershell
# 1. ドライラン（変更内容を確認）
python questions\_fix_answer_leak.py <chapter> --dry-run

# 2. 本番適用（JSON更新 + 該当MP3の自動削除）
python questions\_fix_answer_leak.py <chapter>

# 3. display側の同期
python questions\_audit_display.py <chapter> --apply

# 4. 品質ゲート
python questions\_check_all.py <chapter>
```

> [!IMPORTANT]
> `_fix_answer_leak.py` の `OVERRIDES` は章ごとに書き換える必要がある。
> 新しい章を検証する際は、OVERRIDES を空にしてドライランし、
> 自動修正の結果を確認してから不足分を追加する。

---

## Phase 3：長さバイアスの修正（パディング）

Phase 2 で誤答を短くした結果、正解が突出して長くなる場合がある（length bias）。

### 3.1 パディング方針

- **単なる水増しは禁止**。各パディングは「もっともらしいが誤りの科学的補足」であること
- 生徒が読んだときに「なるほど」と思えるが、実は間違っている内容を追加する
- 正解の長さの±10文字以内を目標とする

### 3.2 パディングデータ作成

```powershell
# 1. パディング対象の抽出
python questions\_dump_for_pads.py <chapter> > _tmp\<chapter>_pad_input.txt

# 2. _pads/<chapter>.json を作成
#    形式: { "qid": { "old_tts_text": "new_longer_tts_text" } }
#    各エントリは教育的に意味のある補足を追加

# 3. 適用（JSON更新 + 該当MP3の自動削除）
python questions\_pad_wrongs_chapter.py <chapter>

# 4. display側の同期
python questions\_audit_display.py <chapter> --apply

# 5. 品質ゲート
python questions\_check_all.py <chapter>
```

### 3.3 パディング品質基準

| ✅ 良い例 | ❌ 悪い例 |
|----------|----------|
| 「水素原子は陽子を一つもつため受け取る側の酸化数を増加させ、酸化に対応する」 | 「これはよく出る問題なので覚えておくとよい」 |
| 「酸性溶液と塩基性溶液では溶解しやすさが異なるため溶液ごとに変わる」 | 「非常に重要な概念である」 |

> [!WARNING]
> パディング内容が正解情報を含まないこと。誤りの主張を補強する方向で
> 追加すること。正解を暴露するパディングは Phase 2 の問題を再発させる。

---

## Phase 4：音声再生成

```powershell
# Phase 2, 3 で削除されたMP3を再生成
python audio\_generate.py <chapter> all

# 総数の確認（50問 × 6ファイル = 300）
(Get-ChildItem -Path "audio\<chapter>" -Recurse -Filter "*.mp3").Count
```

---

## Phase 5：最終品質ゲート

```powershell
python questions\_check_all.py <chapter>
```

以下の全項目をクリアすること：

| 項目 | 基準 |
|------|------|
| `_validate.py` | errors = 0 |
| `_list_rewrite_targets.py` | targets = 0 |
| `_audit_display.py` | fields-needing-conversion = 0 |
| `_length_report.py` | Length-biased (diff>=10) = 0 |
| MP3ファイル数 | 50 × 6 = 300 |

---

## Phase 6：ブラウザスモークテスト

```powershell
python serve.py
```

1. 該当章を選択してクイズを開始
2. 最低10問を実際にプレイし、以下を確認：
   - 選択肢の音声が途中で途切れないこと
   - 正解の選択肢が他の選択肢と比べて明らかに長くないこと
   - 解説音声が最後まで再生されること
   - 選択肢に正解のヒントが含まれていないこと

---

## チェックリスト（コピー用）

```markdown
## <chapter> 詳細検証

- [ ] Phase 1: 全問精読・問題記録
- [ ] Phase 2: 答え漏洩修正
  - [ ] `_fix_answer_leak.py` ドライラン
  - [ ] OVERRIDES 追加（必要に応じて）
  - [ ] 本番適用
  - [ ] `_audit_display.py --apply`
  - [ ] `_check_all.py` PASS
- [ ] Phase 3: 長さバイアス修正
  - [ ] パディングデータ作成
  - [ ] `_pad_wrongs_chapter.py` 適用
  - [ ] `_audit_display.py --apply`
  - [ ] `_check_all.py` PASS（Length-biased = 0）
- [ ] Phase 4: 音声再生成（300 MP3確認）
- [ ] Phase 5: 最終品質ゲート ALL CHECKS PASSED
- [ ] Phase 6: ブラウザスモークテスト
```
