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

## 現在のスコープ

基本チェッカーは共通 AML エンベロープのみを検証します:

* 入力パスが存在すること
* 入力パスがファイルであること
* ファイルが有効な XML であること
* ルート要素が `<AML>` であること
* `<AML>` に直接の子要素 `<Item>` が少なくとも 1 つあること
* `<AML>` の直接の子要素がすべて `<Item>` であること
* すべての直接 `<Item>` に `type` 属性があること
* すべての直接 `<Item>` に `action` 属性があること
* `action` が `add` または `edit` であること
* すべての直接 `<Item>` に `id` 属性があること

## 非対応項目

以下はまだ実装しないでください:

* ItemType 固有のルール
* Action 固有のルール
* Method 固有のルール
* JSON 出力
* 設定ファイル
* 自動修正
* Aras サーバーバリデーション
* パッケージインポートのシミュレーション

将来的に以下のモジュールを追加する可能性があります:

* `itemtype.py`
* `action.py`
* `method.py`

現時点では `base.py` を薄く保ってください。

## コマンド

タスク完了前に必ず以下を実行してください:

```powershell
python -m unittest
python -m aml_harness .\samples\good\base.xml
```

Windows パッケージングの変更がある場合は、さらに以下も実行してください:

```powershell
.\scripts\build_exe.ps1
```

## 安全性

* `.env` ファイルの読み取りや変更は行わないでください。
* 破壊的なコマンドは実行しないでください。
* チェックを通過させるためにテストを削除しないでください。
* 明示的に要求されない限り、新しい依存関係を導入しないでください。
