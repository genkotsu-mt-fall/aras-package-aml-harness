あなたは change-plan.md の内容を、public 配下の Aras 標準パッケージ XML と突合して修正する担当です。

この prompt の前に挿入されている実行コンテキストの `対象タスクディレクトリ` を使ってください。

以下を読んでください。

- 対象タスクディレクトリの change-plan.md
- public/imports.mf
- public 配下の Aras 標準パッケージ XML

## 目的

change-plan.md に書かれている AML 構造、正しい具体例、チェック対象、期待する形式が、public 配下の標準パッケージ XML と矛盾していないか確認し、必要なら change-plan.md を修正してください。

## 更新してよいもの

- 対象タスクディレクトリの change-plan.md

## まだ行ってはいけないこと

- test-cases.md を作成または変更しない。
- aml_harness 配下を変更しない。
- tests を変更しない。
- samples を変更しない。
- Python コードを書かない。
- 外部依存パッケージを追加しない。

## 突合せ観点

- change-plan.md の正しい具体例が、public 配下の標準パッケージ XML に見られる AML パターンと矛盾していないか。
- `Item` の `type`、`action`、`id`、子要素、`Relationships` の階層が標準パッケージ XML の実例と大きくズレていないか。
- `source_id`、`related_id`、`relationship_id`、`propertytype_id` などの参照要素が、標準パッケージ XML の実例と逆向きまたは不自然な前提になっていないか。
- change-plan.md の「対象」と「非対象」が、標準パッケージ XML の実例から見て曖昧すぎないか。
- 標準パッケージ XML で根拠確認できない内容を断定していないか。

## 修正方針

- public 配下の実例で確認できる内容に合わせて、change-plan.md の AML 具体例や説明を修正する。
- 根拠が薄い内容は断定せず、確認事項として書く。
- 変更プランの目的を勝手に広げない。
- 詳細実装やテストケース作成には進まない。
- 読みやすさのため、AML 具体例は XML コードブロックで改行とインデントを整える。

## 作業後に説明すること

1. public 配下で確認した代表的な XML
2. 修正した箇所
3. 断定せず確認事項として残した点
