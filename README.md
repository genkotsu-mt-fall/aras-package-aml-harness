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

テストの実行:

```powershell
python -m unittest
```

チェッカーの実行:

```powershell
python -m aml_harness .\samples\good\base.xml
```

基本チェックの一括実行:

```powershell
.\scripts\check.ps1
```

Manual Agent Loop の 1 ステップ実行:

```powershell
python -m harness.agent_loop
```

このコマンドは、許可済みの検証コマンドだけを実行し、結果を `runs\iteration-N\record.json` に保存します。
検証に失敗した場合は、次に Codex または Copilot Agent へ渡す `prompt.md` も保存します。

## Windows 実行ファイルのビルド

Windows 上で実行:

```powershell
.\scripts\build_exe.ps1
```

出力先:

```txt
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
