# タスク: ItemType の Sequence プロパティ必須チェックを追加する

## 目標

ItemType の Property で Sequence を設定している場合に、`is_required` が必須有効になっているものを最小限検出する。

Sequence は採番値を自動生成する用途で使われるため、対象プロジェクトでは ItemType のプロパティ定義で「必須」にチェックを入れた状態を避ける方針とする。このタスクでは Aras 側の全仕様を再現せず、AML XML 上で明確に判定できる構造だけを対象にする。

注意: `public` 配下の Aras 標準パッケージ XML には、`data_type` が `sequence` で `is_required` が `0` の例だけでなく、`is_required` が `1` の例も存在する。そのため、このチェックは「Aras 標準 XML として常に不正」という判定ではなく、このリポジトリの対象 AML に対する方針チェックとして扱う。

## 参考

参照元:

- `D:\Aras\Dev\04_GitHubCopilot\14_ItemType_Sequence`

確認したサンプル:

- `sample\Import\ItemType\Sample.xml`
- `sample\Import\Sequence\Sample Sequence.xml`

`public` 配下で確認した代表例:

- `public/PLM/Import/ItemType/Simple MCO.xml`
- `public/PLM/Import/ItemType/ECR.xml`
- `public/PLM/Import/ItemType/ECN.xml`
- `public/PLM/Import/ItemType/Simple ECO.xml`
- `public/com/aras/innovator/exchange/ItemType/FileExchangePackage.xml`
- `public/com/aras/innovator/exchange/ItemType/FileExchangeTxn.xml`
- `public/com/aras/innovator/notifications/ItemType/Message.xml`
- `public/com/aras/innovator/masspromote/ItemType/mpo_MassPromotion.xml`

補足: 指定された `public/imports.mf` はこの作業時点の `public` 直下には存在せず、代わりに `public/imports_単数版.mf` と `public/imports_複数版.mf` が存在する。AML 構造の突合は `public` 配下の XML 実体を対象にした。

`public` の標準パッケージ XML では、ItemType の `Relationships` 配下に `Property` が置かれ、Sequence プロパティの代表例は次の構造を持つ。

```xml
<Item type="ItemType" id="2826F2403689438295EDBF60BEAE7C74" action="add">
  <Relationships>
    <Item type="Property" id="88B55ACC92D646D581DDA4565855635B" action="add">
      <data_source keyed_name="Simple MCO">AAF71D8E658E4EFBA36B81941A3851C7</data_source>
      <data_type>sequence</data_type>
      <is_required>0</is_required>
      <source_id keyed_name="Simple MCO" type="ItemType" name="Simple MCO">2826F2403689438295EDBF60BEAE7C74</source_id>
      <name>item_number</name>
    </Item>
  </Relationships>
</Item>
```

一方で、`public/com/aras/innovator/masspromote/ItemType/mpo_MassPromotion.xml` には次のように `sequence` かつ `is_required=1` の標準例がある。

```xml
<Item type="Property" id="1737B093CFF0421E89BC303F884D201D" action="add">
  <data_source keyed_name="mpo_Number">3A3FADE77BAF4DD9A090145885F06CE7</data_source>
  <data_type>sequence</data_type>
  <is_required>1</is_required>
  <source_id keyed_name="mpo_MassPromotion" type="ItemType" name="mpo_MassPromotion">5A549B2EDD3C4CBB9F8797902EE2EBE2</source_id>
  <name>item_number</name>
</Item>
```

## 対象

- AML XML ファイル。
- `Item type="ItemType"` の直下の `Relationships` 配下にある `Item type="Property"`。
- Property の `data_type` が `sequence` のもの。
- `public` では ItemType の `action="add"` と `action="edit"` がどちらも見られるため、親 `ItemType` の `action` は判定条件にしない。ただし、確認済みの Sequence プロパティ代表例は `Item type="Property" action="add"` である。
- `data_source` は参照先 Sequence の ID と `keyed_name` を持つ要素として扱い、`source_id` は Property が属する ItemType を指す要素として扱う。

## 非対象

- `Item type="Sequence"` そのものの定義。
- `ItemType` 配下ではない `Item type="Property"`。
- `RelationshipType` 定義配下の Property。`public/PLM/Import/RelationshipType/Part BOM.xml` などでは `relationship_id` 配下に関係用の `ItemType` と `Property` が出るが、このタスクでは ItemType の Sequence プロパティ必須チェックを最小実装する範囲に限定する。
- `source_id`、`related_id`、`relationship_id`、`propertytype_id` などの参照整合性そのものの検証。

## 最小チェック要求

### エラーにする

- `Item type="Property"` の `data_type` が `sequence`。
- かつ `is_required` の値が `1`。
- ただし、この条件に一致する XML が Aras 標準パッケージにも存在するため、診断メッセージでは Aras 標準仕様違反と断定しない。

### エラーにしない

- `data_type` が `sequence` で、`is_required` が `0`。
- `data_type` が `sequence` ではない Property。
- `ItemType` 配下ではない Property。

## メッセージ案

```txt
error ITYPE_SEQUENCE001 Sequence property must not be required
```

## 実装メモ

- 新しいランタイム依存関係は追加しない。
- Python 標準ライブラリのみで実装する。
- 既存の XML 走査と診断出力の形式に合わせる。
- `is_required` が存在しない場合をこのタスクでエラーにするかは未確定。ミニマム要求では `is_required` が明示的に `1` の場合だけを検出する。
- `data_source` が実在する Sequence を指すかどうかは、このタスクでは確認しない。
- Property が `action="edit"` で `data_type=sequence` に変更される AML を検出対象に含めるかは確認事項。`public` の確認済み代表例では Sequence プロパティは `action="add"` だったため、初期実装で親 `ItemType` の action だけを無視するのか、Property 自身の action も無視するのかを決める必要がある。

## テスト観点

- `data_type=sequence` かつ `is_required=1` の Property でエラーになる。
- `data_type=sequence` かつ `is_required=0` の Property でエラーにならない。
- `data_type=string` など Sequence 以外の Property で `is_required=1` でもこのルールではエラーにならない。
- `ItemType` 配下ではない Property は、このルールではエラーにならない。
