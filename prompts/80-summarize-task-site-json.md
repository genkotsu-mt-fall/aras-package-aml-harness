あなたは `tasks/` 配下の開発タスク成果物を、静的サイトで表示するための JSON に要約する担当です。

この prompt の前に挿入されている実行コンテキストの `対象タスクディレクトリ` を使ってください。

以下を読んでください。

- 対象タスクディレクトリの `change-plan.md`
- 対象タスクディレクトリに存在する `test-cases.md`
- 対象タスクディレクトリに存在する `test-cases-review*.md`
- 対象タスクディレクトリに存在する `test-code-review*.md`
- 対象タスクディレクトリに存在する `public-check*.md`
- 必要に応じて、変更内容を理解するための `tests/`, `samples/`, `aml_harness/`

## 目的

各タスクが以下をどう進めたのか、静的サイトで一覧・詳細表示できるように整理してください。

- どんな変更プランを持っていたか
- どんなレビューを経たか
- どんなテストや実装を追加・変更したか
- public 標準パッケージ確認で何が分かったか

## 作成または更新するファイル

対象タスクディレクトリ名を使い、以下の JSON ファイルを作成または更新してください。

- `docs/task-site/data/<task-dir-basename>.json`

例:

- 対象タスクディレクトリが `tasks/task-010` の場合、出力先は `docs/task-site/data/task-010.json`

## 重要な制約

- `docs/task-site/data/<task-dir-basename>.json` 以外を変更しない。
- `tasks/` 配下の成果物を変更しない。
- `aml_harness/`, `tests/`, `samples/`, `public/` を変更しない。
- `.env` を読まない。
- 事実が成果物から読み取れない場合は推測で断定せず、`不明` または空配列にする。
- JSON 以外の説明文をファイルへ混ぜない。

## JSON 形式

次の形を守ってください。

```json
{
  "task_id": "task-010",
  "title": "短い日本語タイトル",
  "status": "完了|要確認|不明",
  "summary": "タスク全体を 2 文以内で要約する。",
  "change_plan": {
    "background": "背景を 2 文以内で要約する。",
    "goal": "達成したい変更を 2 文以内で要約する。",
    "scope": ["対象範囲を短く列挙する"],
    "out_of_scope": ["非対象が分かる場合だけ列挙する"]
  },
  "reviews": [
    {
      "kind": "test-cases|test-code|public-check",
      "file": "tasks/task-010/test-code-review001.md",
      "judgement": "OK|修正が必要|不明",
      "findings": ["主要な指摘や確認結果を短く列挙する"],
      "result": "レビュー後にどう扱われたかを短く書く"
    }
  ],
  "implementation": {
    "tests": ["追加・変更されたテスト観点を短く列挙する"],
    "samples": ["追加・変更された sample AML を短く列挙する"],
    "app": ["aml_harness 側の実装変更を短く列挙する"],
    "verification": ["実行・確認された検証を短く列挙する"]
  },
  "artifacts": [
    {
      "label": "change-plan.md",
      "path": "tasks/task-010/change-plan.md",
      "type": "change-plan"
    }
  ],
  "updated_at": "YYYY-MM-DD"
}
```

## 書き方

- `title` は `change-plan.md` の見出しから自然に作る。
- `reviews` はファイル名順に並べる。
- `artifacts` には、対象タスクディレクトリに存在する主要成果物を含める。
- `implementation.tests`, `implementation.samples`, `implementation.app` は、成果物から読み取れる範囲で具体化する。
- JSON 文字列中の改行は避け、1 項目を短くしてください。
