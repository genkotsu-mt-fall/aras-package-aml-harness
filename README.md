# aras-package-aml-harness

Aras Innovator のパッケージを Codex、Claude Code、GitHub Copilot などのコーディング AI エージェントで作成・変更する際に、ItemType ごとに特有の AML 記述ルールが正しいかをチェックするリンターです。

## ダウンロード

GitHub Releases の Release asset から以下のファイルをダウンロードして使用してください。

```txt
aml-harness.exe
```

GitHub Releases に表示される `Source Code (zip)` や `Source Code (tar.gz)` はソースコードのアーカイブです。Windows 実行ファイルとして使う場合は、Assets にある `aml-harness.exe` をダウンロードしてください。

## 使い方

`aml-harness.exe` をダウンロードし、PowerShell またはコマンドプロンプトで以下を実行します。

```powershell
.\aml-harness.exe .\ItemType\Part.xml
```

複数ファイルをまとめてチェックする場合:

```powershell
.\aml-harness.exe .\ItemType\*.xml
```

## 実行結果

### 正常

```txt
AML base check passed. 561 file(s) checked.
```

### 失敗

```txt
C:\Aras\Packages\SampleProject\Import\ItemType\Sample_Customer.xml:1:1 error ITYPE_SEQUENCE001 Sequence property must not be required

AML base check failed. 1 error(s).
```

## 開発者向け情報

このプロジェクトの開発方法については、以下を参照してください。

* [scripts/README.md](./scripts/README.md)

## 変更履歴・タスク履歴

このプロジェクトの変更履歴やタスク履歴は、以下の GitHub Pages で確認できます。

https://genkotsu-mt-fall.github.io/aras-package-aml-harness/task-site/
