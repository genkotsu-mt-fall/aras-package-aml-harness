あなたは public 標準パッケージ検証結果を、次のタスクの change-plan.md へ昇格する担当です。

この prompt の前に挿入されている実行コンテキストを使ってください。
追加命令に `入力 public-check` と `出力 change-plan` が示されている場合は、そのパスを優先してください。

以下を読んでください。

- 入力 public-check*.md
- 入力元タスクの change-plan.md
- 入力元タスクの test-cases.md があれば読む

## 目的

public-check*.md の失敗ケースや標準 XML との不整合を、次に実装すべき修正タスクの change-plan.md として整理してください。

## 作成または更新してよいもの

- 出力先タスクディレクトリの change-plan.md

## まだ行ってはいけないこと

- public 配下を変更しない。
- aml_harness 配下を変更しない。
- tests を変更しない。
- samples を変更しない。
- test-cases.md を作成しない。
- Python コードを書かない。
- 外部依存パッケージを追加しない。

## 昇格方針

- public-check*.md の判定が OK の場合は、原則として新しい修正タスクを作らない。必要なら change-plan.md に「対応不要」と明記する。
- public-check*.md の判定が 修正が必要 の場合は、失敗ケースを次タスクの目標、修正対象、完了条件へ落とし込む。
- public XML は原則として正しい入力として扱い、失敗は過検出または実装ルールの過剰さとして整理する。
- 入力元タスクの目的を踏まえるが、次タスクで直す範囲を広げすぎない。
- public-check*.md に根拠がない推測は断定せず、確認事項として残す。

## change-plan.md の形式

日本語で、以下の構成にしてください。

# タスク: public 標準パッケージ検証で見つかった過検出の修正

## 目標

## 背景

- 入力元タスク
- 入力 public-check

## 失敗ケース

public-check*.md の失敗ケースを要約する。

## 修正対象

## 非対象

- public 配下の XML は変更しない。
- テストを弱めない。
- 入力元タスクの目的を超える新規ルールは追加しない。

## 実装方針

## 完了条件

- public-check*.md の失敗ケースが解消していること。
- `python -m unittest` が成功すること。
- `python -m aml_harness .\samples\good\base.xml` が成功すること。
- 対象 public XML の再検証が成功すること。

## 確認事項

断定できない点があれば書く。

## 作業後に説明すること

1. 昇格した失敗ケース
2. 次タスクの修正範囲
3. 確認事項
