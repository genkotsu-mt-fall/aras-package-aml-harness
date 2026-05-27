# AGENTS.md

## プロジェクト概要

このリポジトリは `aras-package-aml-harness` です。

以下の名称の最小構成 Windows CLI ツールを提供します:

```txt
aml-harness.exe
```

このツールは、Aras Innovator パッケージ開発向け AML XML ファイルの基本構造を検証します。

## ランタイム

チェッカーの実装には Python 標準ライブラリのみを使用してください。

使用可能な標準ライブラリモジュール:

* `pathlib`
* `sys`
* `glob`
* `dataclasses`
* `xml.etree.ElementTree`
* `unittest`

ランタイム依存関係は追加しないでください。

`PyInstaller` は `aml-harness.exe` の作成に使う開発／ビルド依存関係としてのみ許可されています。

## 安全性

* `.env` ファイルの読み取りや変更は行わないでください。
* 破壊的なコマンドは実行しないでください。
* チェックを通過させるためにテストを削除しないでください。
* 明示的に要求されない限り、新しい依存関係を導入しないでください。
