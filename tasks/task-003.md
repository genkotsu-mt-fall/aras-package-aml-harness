# タスク 003: Form XML の標準プロパティ propertytype_id チェック追加

## 目標

`Form/*.xml` 専用のチェック処理を追加します。

`aml_harness/base.py` は、簡単な AML / Item の確認を行う、すべての AML に対するベースチェッカーです。
今回の Form 固有ルールは、ベースチェッカーを薄く保ちながら追加してください。

関連 Issue:

```txt
https://github.com/genkotsu-mt-fall/aras-package-aml-harness/issues/3
```

## 正しい具体例

```txt
D:\Aras\Dev\04_GitHubCopilot\35_ItemType_標準属性セット\sample\Import\Form\Sample.xml
```

## チェック内容

### Form add 配下の Field

以下の構造を対象にします。

```txt
AML
  Item type="Form" action="add"
    Relationships
      Item type="Body"
        Relationships
          Item type="Field"
            propertytype_id
```

この位置にある `Item type="Field"` では、対象の標準プロパティに対する `propertytype_id` はインラインGETではなく、32桁GUIDであることを確認してください。

### Field edit

以下の構造を対象にします。

```txt
AML
  Item type="Field" action="edit"
    propertytype_id
```

この位置にある対象の標準プロパティでは、`propertytype_id` がインラインGETであることを確認してください。

## 対象プロパティ

```powershell
$StandardProperties = @(
  'classification',
  'config_id',
  'created_by_id',
  'created_on',
  'css',
  'current_state',
  'generation',
  'id',
  'is_current',
  'is_released',
  'keyed_name',
  'locked_by_id',
  'major_rev',
  'managed_by_id',
  'minor_rev',
  'modified_by_id',
  'modified_on',
  'new_version',
  'not_lockable',
  'owned_by_id',
  'permission_id',
  'state',
  'team_id',
  'effective_date',
  'release_date',
  'superseded_date'
)
```

## 実装方針

* Python 標準ライブラリだけを使ってください。
* 既存の AML ベースチェックは壊さないでください。
* `base.py` を過度に大きくしないでください。
* Form 固有チェック用のモジュールを追加してよいです。
* テストを追加し、対象標準プロパティの `propertytype_id` 形式違反を検出できることを確認してください。
* テストを削除したり、スキップしたり、アサーションを弱めたりしないでください。

## 完了条件

以下を満たしてください。

* `Form/*.xml` 専用チェックが追加されていること
* Form add 配下の対象標準プロパティでは、`propertytype_id` が32桁GUIDであることを検証できること
* Field edit の対象標準プロパティでは、`propertytype_id` がインラインGETであることを検証できること
* 既存の AML ベースチェックが引き続き成功すること

以下のコマンドが正常に終了すること:

```powershell
python -m unittest
python -m aml_harness .\samples\good\base.xml
```
