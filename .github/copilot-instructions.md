`AGENTS.md` に従ってください。

このリポジトリは、Aras Innovator パッケージファイル向けの最小構成 AML XML ハーネスをビルドします。

最終的な Windows 実行ファイル:

```txt
aml-harness.exe
```

変更は小さくテスト可能な単位に保ってください。

タスク完了前に必ず以下を実行してください:

```powershell
python -m unittest
python -m aml_harness .\samples\good\base.xml
```

サードパーティのランタイム依存関係は追加しないでください。
