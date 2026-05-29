# aras-package-aml-harness

Aras Innovator パッケージファイル向けの最小構成 AML XML ハーネスです。

配布する Windows 実行ファイル:

```txt
aml-harness.exe
```

## 目的

このツールは、Aras Innovator パッケージ向けに生成された AML XML ファイルの基本構造を検証します。

AI が生成した AML XML ファイルに対する小規模な機械的品質ゲートとして機能することを目的としています。

## 現在のチェック項目

基本チェッカーが検証する内容:

* 入力ファイルが存在すること
* 入力パスがファイルであること
* 入力ファイルが有効な XML であること
* ルート要素が `<AML>` であること
* `<AML>` に直接の子要素 `<Item>` が少なくとも 1 つあること
* `<AML>` の直接の子要素がすべて `<Item>` であること
* すべての直接 `<Item>` に `type` 属性があること
* すべての直接 `<Item>` に `action` 属性があること
* `action` が `add` または `edit` であること
* すべての直接 `<Item>` に `id` 属性があること

## 非対応項目

このツールはまだ以下を検証しません:

* ItemType 固有のルール
* Action 固有のルール
* Method 固有のルール
* Aras サーバー側の妥当性
* パッケージインポートのシミュレーション

## 開発

```powershell
# テストの実行
python -m unittest

# チェッカーの実行
python -m aml_harness .\samples\good\base.xml

# 基本チェックの一括実行
.\scripts\check.ps1

# Manual Agent Loop の 1 ステップ実行
# 許可済みの検証コマンドだけを実行し、
# 結果を runs\iteration-N\record.json に保存する。
# 検証に失敗した場合は、次に Codex または Copilot Agent へ渡す
# prompt.md も保存する。
python -m harness.agent_loop
```

## Codex 開発フロー

タスクごとに `change-plan.md` から開始し、以下の順で実行します。

```bash
# 1. change-plan.md を作成する
#    入力: なし
#    出力: tasks/task-001/change-plan.md
mkdir -p tasks/task-001
vi tasks/task-001/change-plan.md

# 1.5. change-plan.md を public の標準パッケージ XML と突合して修正する
#      prompt: prompts/05-align-change-plan-with-public.md
#      更新: tasks/task-001/change-plan.md
scripts/05-align-change-plan-with-public.sh tasks/task-001

# 2. test-cases.md を作成する
#    prompt: prompts/10-create-test-cases.md
#    出力: tasks/task-001/test-cases.md
scripts/10-create-test-cases.sh tasks/task-001

# 3. test-cases.md をレビューする
#    prompt: prompts/11-review-test-cases.md
#    出力: tasks/task-001/test-cases-review001.md
scripts/11-review-test-cases.sh tasks/task-001 001

#    custom agent を使う場合:
#    prompt: prompts/11-review-test-cases-with-agent.md
#    agent : .codex/agents/test_cases_reviewer.toml
scripts/codex-run.sh read-only prompts/11-review-test-cases-with-agent.md tasks/task-001 001 > tasks/task-001/test-cases-review001.md

# 4. レビュー指摘を test-cases.md に反映する
#    prompt: prompts/12-apply-test-cases-review.md
#    入力: tasks/task-001/test-cases-review001.md
#    更新: tasks/task-001/test-cases.md
scripts/12-apply-test-cases-review.sh tasks/task-001 001

# 5. test-cases.md から unittest を実装する
#    prompt: prompts/20-implement-unittest-from-test-cases.md
#    主な更新対象: tests/, samples/
scripts/20-implement-tests.sh tasks/task-001

# 6. テストコードをレビューする
#    prompt: prompts/30-review-test-code.md
#    出力: tasks/task-001/test-code-review001.md
scripts/30-review-tests.sh tasks/task-001 001

# 7. テストコードレビュー指摘を反映する
#    prompt: prompts/31-apply-test-code-review.md
#    入力: tasks/task-001/test-code-review001.md
#    主な更新対象: tests/, samples/
scripts/31-apply-test-code-review.sh tasks/task-001 001

# 8. 失敗しているテストに対してアプリを実装する
#    prompt: prompts/50-implement-app-from-failing-tests.md
#    主な更新対象: aml_harness/
scripts/50-implement-app.sh tasks/task-001

# 9. public 標準パッケージ XML で過検出がないか確認する
#    prompt: prompts/60-check-public-from-change-plan.md
#    例: Form 機能なら public/PLM/Import/Form/*.xml を確認する
#    出力: tasks/task-001/public-check001.md
scripts/60-check-public.sh tasks/task-001 001

# 10. Harness の最終検証を実行する
#    内部で python -m unittest と
#    python -m aml_harness .\samples\good\base.xml を実行する
scripts/90-harness.sh

# public-check で修正が必要になった場合は、次タスクの change-plan.md へ昇格する
#    prompt: prompts/70-promote-public-check-to-change-plan.md
#    入力: tasks/task-001/public-check001.md
#    出力: 次の tasks/task-NNN/change-plan.md
scripts/70-promote-public-check.sh tasks/task-001 001
```

一括実行する場合は、レビュー成果物の `## 判定` を見ながら、上限付きでレビューと反映を繰り返します。
レビュー成果物は `## 判定` の次の非空行に `OK` または `修正が必要` が必要です。

```bash
scripts/run-task.sh tasks/task-001

# レビューループ上限を変える場合
MAX_REVIEW_LOOPS=5 scripts/run-task.sh tasks/task-001

# public-check で修正が必要な場合に次タスクへ遷移する上限を変える場合
MAX_TASK_CHAIN=5 scripts/run-task.sh tasks/task-001

# 全工程に追加命令を渡す場合
scripts/run-task.sh tasks/task-001 "public の標準 XML との不整合を優先して確認する"
```

各 Codex 実行スクリプトには、最後の引数として追加命令を渡せます。

```bash
scripts/10-create-test-cases.sh tasks/task-001 "AML パターン例は短く、表の下に整形して書く"
scripts/11-review-test-cases.sh tasks/task-001 001 "public 配下の Form XML を重点的に確認する"
scripts/20-implement-tests.sh tasks/task-001 "test_base.py は薄く保つ"
scripts/60-check-public.sh tasks/task-001 001 "Form 機能なので public/PLM/Import/Form/*.xml を確認する"
```

## タスク履歴サイト

`tasks/` 配下の各タスクについて、変更プラン、レビュー、実装内容を静的サイトで確認できます。

```bash
# 差分チェックだけ行う
scripts/80-check-task-site.sh

# 変更があった task だけ Codex で JSON 要約を生成する
scripts/80-update-task-site.sh

# 1 task だけ再生成する
scripts/80-summarize-task-site.sh tasks/task-010

# manifest だけ作り直す
scripts/81-build-task-site-manifest.sh
```

サイト本体は `docs/task-site/index.html` です。`fetch` で `docs/task-site/data/*.json` を読むため、リポジトリルートをローカル HTTP サーバーで配信し、`/docs/task-site/index.html` を開いてください。

## Windows 実行ファイルのビルド

```powershell
# Windows 上で実行
.\scripts\build_exe.ps1

# 出力先
dist\aml-harness.exe
```

## 使い方

```powershell
.\aml-harness.exe .\ItemType\Part.xml
```

複数ファイルの場合:

```powershell
.\aml-harness.exe .\ItemType\*.xml
```
