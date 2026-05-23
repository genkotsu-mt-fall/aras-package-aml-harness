# タスク 001: 最小構成 AML 基本チェッカーの作成

## 目標

`aras-package-aml-harness` 向けの最小構成 Python AML XML 基本チェッカーを作成します。

最終的な Windows 実行ファイル名:

```txt
aml-harness.exe
```

## 必要な動作

以下の開発用コマンドが動作すること:

```powershell
python -m aml_harness <xml-file>
```

チェッカーは AML の基本構造のみを検証します:

* ファイルが存在すること
* パスがファイルであること
* ファイルが有効な XML であること
* ルート要素が `<AML>` であること
* `<AML>` に直接の子要素 `<Item>` が少なくとも 1 つあること
* `<AML>` の直接の子要素がすべて `<Item>` であること
* すべての直接 `<Item>` に `type` 属性があること
* すべての直接 `<Item>` に `action` 属性があること
* すべての直接 `<Item>` の `action` が `add` または `edit` であること
* すべての直接 `<Item>` に `id` 属性があること

## 非対応項目

以下はまだ実装しないでください:

* ItemType 固有のチェック
* Action 固有のチェック
* Method 固有のチェック
* JSON 出力
* 設定ファイルのサポート
* 自動修正
* Aras サーバーバリデーション
* パッケージインポートのシミュレーション

## 完了条件

以下のコマンドが正常に終了すること:

```powershell
python -m unittest
python -m aml_harness .\samples\good\base.xml
```
