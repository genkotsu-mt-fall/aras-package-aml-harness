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

## チェック項目

`aml_harness/` で実装しているチェック項目は以下のとおりです。
空文字または空白のみの子要素は、必須チェックでは未設定として扱います。

| 分類 | エラーコード | 適用対象 | チェック内容 |
| --- | --- | --- | --- |
| ファイル | FILE001 | 指定パス | ファイルまたはパスが存在すること |
| ファイル | FILE002 | 指定パス | 指定パスがファイルであること |
| ファイル | FILE003 | 指定パス | UTF-8 テキストとして読み取れること |
| XML | AML000 | すべての入力ファイル | XML としてパースできること |
| AML 基本構造 | AML001 | `imports.mf` 以外 | ルート要素が `<AML>` であること |
| AML 基本構造 | AML002 | `<AML>` | 1 つ以上の `<Item>` を直接含むこと |
| AML 基本構造 | AML003 | `<AML>` の直接子要素 | 直接子要素が `<Item>` であること |
| AML 基本構造 | AML004 | `<Item>` | `type` 属性を持つこと |
| AML 基本構造 | AML005 | `<Item>` | `action` 属性を持ち、値が `add`, `edit`, `delete`, `get` のいずれかであること |
| AML 基本構造 | AML006 | `action="add"` または `action="edit"` の `<Item>` | `id` 属性を持つこと |
| AML 基本構造 | AML007 | `action="delete"` の `<Item>` | 空でない `where` 属性を持つこと |
| imports.mf | IMPORTS001 | `imports.mf` | ルート要素が `<imports>` であること |
| imports.mf | IMPORTS002 | `<imports>` | 1 つ以上の `<package>` を直接含むこと |
| imports.mf | IMPORTS003 | `<imports>` の直接子要素 | 直接子要素が `<package>` であること |
| imports.mf | IMPORTS004 | `<package>` | `name` 属性を持つこと |
| imports.mf | IMPORTS005 | `<package>` | `path` 属性を持つこと |
| imports.mf | IMPORTS006 | `<package path="...">` | `path` が `.`, `./`, `.\` 以外の場合、`imports.mf` からの相対パスとして存在すること |
| imports.mf | IMPORTS007 | `<package>` 直下の `<dependson>` | `name` 属性を持つこと |
| Action | ACTION_LIST001 | `Action` フォルダーの `type="Action"` の `<Item>` | `<location>` が `client`, `server` のいずれかであること |
| Action | ACTION_LIST002 | `Action` フォルダーの `type="Action"` の `<Item>` | `<target>` が `main`, `window`, `one window`, `none` のいずれかであること |
| Action | ACTION_LIST003 | `Action` フォルダーの `type="Action"` の `<Item>` | `<type>` が `generic`, `item`, `itemtype`, `url` のいずれかであること |
| ItemType | ITEMTYPE001 | `ItemType` フォルダーの `ItemType` 配下にある `Property action="add"` | 標準プロパティは `Property action="edit"` で記述すること。対象は `classification`, `created_by_id`, `created_on`, `current_state`, `generation`, `locked_by_id`, `major_rev`, `managed_by_id`, `modified_by_id`, `modified_on`, `owned_by_id`, `state`, `superseded_date` |
| ItemType | ITYPE_SEQUENCE001 | `ItemType action="add"` または `action="edit"` 配下の `Property action="add"` | `<data_type>sequence</data_type>` のプロパティは `<is_required>1</is_required>` にしないこと。ただし `ItemType/mpo_MassPromotion.xml` は除外 |
| ItemType パッケージ | ITEMTYPE_SERVER_EVENT_REQUIRED001 | `ItemType` フォルダーの `Server Event action="add"` | `<event_version>` と `<source_id>` を持つこと |
| ItemType パッケージ | ITEMTYPE_SERVER_EVENT_LIST001 | `ItemType` フォルダーの `Server Event` | `<behavior>` がある場合、`float`, `fixed`, `hard_fixed`, `hard_float` のいずれかであること |
| ItemType パッケージ | ITEMTYPE_ITEM_ACTION_REQUIRED001 | `ItemType` フォルダーの `Item Action action="add"` | `<source_id>` を持つこと |
| ItemType パッケージ | ITEMTYPE_ITEM_ACTION_LIST001 | `ItemType` フォルダーの `Item Action` | `<behavior>` がある場合、`float`, `fixed`, `hard_fixed`, `hard_float` のいずれかであること |
| Form | FORM001 | `Form` フォルダーの `Field action="add"` | `<propertytype_id>` を持つ場合、値が 32 桁の 16 進 GUID であること |
| Form | FORM002 | `Form` フォルダーの `Field action="add"` | 標準プロパティの `<propertytype_id>` を直接持たないこと |
| Form | FORM003 | `Form` フォルダーの `Field action="edit"` | 標準プロパティの `propertytype_id/Item` を編集する場合、同じ `id` の `Field action="add"` が存在すること |
| Form | FORM004 | `Form` フォルダーの `Field action="edit"` | 標準プロパティの `propertytype_id/Item` は `type="Property"`, `action="get"`, `select="id"` であること |
| Form | FORM006 | `Form` フォルダーの `Field action="edit"` | 標準プロパティの `propertytype_id/Item/source_id` は `type="ItemType"` であること |
| Form パッケージ | FORM_REQUIRED001 | `Form` フォルダーの `Form action="add"` | `<height>`, `<width>`, `<name>` を持つこと |
| Form パッケージ | FORM_BODY_REQUIRED001 | `Form` フォルダーの `Body action="add"` | `<source_id>` を持つこと |
| Form パッケージ | FORM_BODY_LIST001 | `Form` フォルダーの `Body` | `<behavior>` は `float`, `fixed`, `hard_fixed`, `hard_float`、`<bg_attach>` は `fixed`, `scroll`、`<bg_repeat>` は `no-repeat`, `repeat`, `repeat-x`, `repeat-y` のいずれかであること |
| Form パッケージ | FORM_FIELD_REQUIRED001 | `Form` フォルダーの `Field action="add"` | `<show_help>` と `<source_id>` を持つこと |
| Form パッケージ | FORM_FIELD_LIST001 | `Form` フォルダーの `Field` | `<behavior>`, `<field_type>`, `<font_weight>`, `<label_position>`, `<display_length_unit>`, `<clip_overflow>`, `<orientation>`, `<positioning>`, `<text_align>` がある場合、定義済みの値であること |
| Form パッケージ | FORM_FIELD_EVENT_REQUIRED001 | `Form` フォルダーの `Field Event action="add"` | `<source_id>` を持つこと |
| Form パッケージ | FORM_FIELD_EVENT_LIST001 | `Form` フォルダーの `Field Event` | `<field_event>` が `onblur`, `onfocus`, `onchange`, `onclick`, `ondblclick`, `onselect` のいずれかで、`<behavior>` がある場合は定義済みの値であること |
| Form パッケージ | FORM_FORM_EVENT_REQUIRED001 | `Form` フォルダーの `Form Event action="add"` | `<source_id>` を持つこと |
| Form パッケージ | FORM_FORM_EVENT_LIST001 | `Form` フォルダーの `Form Event` | `<form_event>` が定義済みのフォームイベント名で、`<behavior>` がある場合は定義済みの値であること |
| Method パッケージ | METHOD_REQUIRED001 | `Method` フォルダーの `Method action="add"` | `<execution_allowed_to>` と `<name>` を持つこと |
| Method パッケージ | METHOD_LIST001 | `Method` フォルダーの `Method` | `action="get"` 以外の場合、`<method_location>` があるなら `client`, `server` のいずれかであること |
| RelationshipType パッケージ | RELTYPE_SERVER_EVENT_REQUIRED001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Server Event action="add"` | `<event_version>` と `<source_id>` を持つこと |
| RelationshipType パッケージ | RELTYPE_SERVER_EVENT_LIST001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Server Event` | `<behavior>` がある場合、`float`, `fixed`, `hard_fixed`, `hard_float` のいずれかであること |
| RelationshipType パッケージ | RELTYPE_ITEM_ACTION_REQUIRED001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Item Action action="add"` | `<source_id>` を持つこと |
| RelationshipType パッケージ | RELTYPE_ITEM_ACTION_LIST001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Item Action` | `<behavior>` がある場合、`float`, `fixed`, `hard_fixed`, `hard_float` のいずれかであること |
| RelationshipType パッケージ | RELTYPE_BODY_REQUIRED001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Body action="add"` | `<source_id>` を持つこと |
| RelationshipType パッケージ | RELTYPE_BODY_LIST001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Body` | `<behavior>`, `<bg_attach>`, `<bg_repeat>` がある場合、定義済みの値であること |
| RelationshipType パッケージ | RELTYPE_FIELD_REQUIRED001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Field action="add"` | `<show_help>` と `<source_id>` を持つこと |
| RelationshipType パッケージ | RELTYPE_FIELD_LIST001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Field` | `<behavior>`, `<field_type>`, `<font_weight>`, `<label_position>`, `<display_length_unit>`, `<clip_overflow>`, `<orientation>`, `<positioning>`, `<text_align>` がある場合、定義済みの値であること |
| RelationshipType パッケージ | RELTYPE_FIELD_EVENT_REQUIRED001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Field Event action="add"` | `<source_id>` を持つこと |
| RelationshipType パッケージ | RELTYPE_FIELD_EVENT_LIST001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Field Event` | `<field_event>` と `<behavior>` がある場合、定義済みの値であること |
| RelationshipType パッケージ | RELTYPE_FORM_EVENT_REQUIRED001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Form Event action="add"` | `<source_id>` を持つこと |
| RelationshipType パッケージ | RELTYPE_FORM_EVENT_LIST001 | `RelationshipType` フォルダー内の関連 ItemType 配下の `Form Event` | `<form_event>` と `<behavior>` がある場合、定義済みの値であること |
| List パッケージ | LIST_REQUIRED001 | `List` フォルダーの `List action="add"` | `<name>` を持つこと |
| Variable パッケージ | VARIABLE_REQUIRED001 | `Variable` フォルダーの `Variable action="add"` | `<name>` を持つこと |
| UserMessage パッケージ | USERMESSAGE_REQUIRED001 | `UserMessage` フォルダーの `UserMessage action="add"` | `<name>` を持つこと |
| Life Cycle Map パッケージ | LIFECYCLE_REQUIRED001 | `Life Cycle Map` フォルダーの `Life Cycle Map action="add"` | `<name>` を持つこと |

### 列挙値の詳細

`FORM_FIELD_LIST001` と `RELTYPE_FIELD_LIST001` で使用する `Field` の列挙値は以下です。

| 子要素 | 許可値 |
| --- | --- |
| `behavior` | `float`, `fixed`, `hard_fixed`, `hard_float` |
| `field_type` | `button`, `checkbox`, `checkbox list`, `class structure`, `color`, `color list`, `date`, `dropdown`, `file item`, `formatted text`, `groupbox`, `html`, `image`, `item`, `label`, `listbox multi select`, `listbox single select`, `ml_string`, `nested form`, `password`, `radio button list`, `textarea`, `text` |
| `font_weight` | `bold`, `normal` |
| `label_position` | `bottom`, `left`, `right`, `top` |
| `display_length_unit` | `%`, `px` |
| `clip_overflow` | `hidden`, `visible` |
| `orientation` | `horizontal`, `vertical` |
| `positioning` | `absolute`, `relative`, `static` |
| `text_align` | `center`, `left`, `right` |

`FORM_FORM_EVENT_LIST001` と `RELTYPE_FORM_EVENT_LIST001` で使用する `form_event` の許可値は以下です。

```txt
onformpopulated, onload, onbeforeunload, onunload, onresize,
onbeforeprint, onafterprint, oncontextmenu, onkeydown, onkeyup,
onmouseover, onmousedown, onmouseup, onmousemove
```

パッケージ固有チェックは、`samples` 配下の XML ファイルには適用されません。

## 開発者向け情報

このプロジェクトの開発方法については、以下を参照してください。

* [scripts/README.md](./scripts/README.md)

## 変更履歴・タスク履歴

このプロジェクトの変更履歴やタスク履歴は、以下の GitHub Pages で確認できます。

https://genkotsu-mt-fall.github.io/aras-package-aml-harness/task-site/

## 免責事項

本プロジェクトは Aras Corporation の公式製品ではなく、Aras Corporation、その関連会社、Aras Labs によって承認・後援・推奨されているものではありません。詳細は [DISCLAIMER.md](./DISCLAIMER.md) を参照してください。
