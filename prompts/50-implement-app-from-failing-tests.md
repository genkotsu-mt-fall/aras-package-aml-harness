あなたは失敗している unittest に対して、アプリ側を最小実装する担当です。

この prompt の前に挿入されている実行コンテキストの `対象タスクディレクトリ` を使ってください。

以下を読んでください。

- 対象タスクディレクトリの change-plan.md
- 対象タスクディレクトリの test-cases.md
- tests 配下
- samples 配下
- aml_harness 配下

## 目的

失敗している unittest を通すために、aml_harness 配下を最小限だけ修正してください。

## 更新してよいもの

- aml_harness 配下

## 原則

- Python 標準ライブラリだけを使う。
- 外部依存パッケージを追加しない。
- tests を変更しない。
- samples を変更しない。
- test-cases.md の非対象を勝手に実装しない。
- 既存コードの構成に合わせる。
- 不要なリファクタリングをしない。

## 作業後に実行すること

```powershell
python -m unittest
python -m aml_harness .\samples\good\base.xml
```

失敗した場合は、残っている失敗理由を説明してください。
