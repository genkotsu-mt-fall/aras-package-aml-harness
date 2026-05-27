# タスク 006: ItemType XML の Property 配置チェック追加

## 目的

`ItemType/*.xml` で、標準プロパティと ItemType 固有プロパティの `Property` 配置を検査する。

## 期待する構造

- 標準プロパティの既存定義を上書きする場合は、別の `ItemType action="edit"` 配下の `Relationships/Item type="Property" action="edit"` に置く。
- 標準プロパティの `Property action="edit"` は、標準パッケージ XML では `where="source_id='...' and name='...'"` と、同じ ItemType を指す `source_id` 子要素を持つ形が見られる。
- ItemType 固有プロパティを新規追加する場合は `Relationships/Item type="Property" action="add"` に置く。親の `ItemType` は `action="add"` だけでなく、標準パッケージ XML では `action="edit"` の例もあるため、親 `ItemType` の `action` だけでは失敗判定しない。

標準プロパティ上書きの例:

```xml
<AML>
  <Item type="ItemType" id="4F1AC04A2B484F3ABA4E20DB63808A88" action="edit">
    <Relationships>
      <Item type="Property" action="edit" where="source_id='4F1AC04A2B484F3ABA4E20DB63808A88' and name='state'">
        <column_alignment>left</column_alignment>
        <column_width>80</column_width>
        <data_type>string</data_type>
        <source_id keyed_name="Part" type="ItemType" name="Part">4F1AC04A2B484F3ABA4E20DB63808A88</source_id>
        <name>state</name>
      </Item>
    </Relationships>
  </Item>
</AML>
```

ItemType 固有プロパティ追加の例:

```xml
<AML>
  <Item type="ItemType" id="4F1AC04A2B484F3ABA4E20DB63808A88" action="add">
    <name>Part</name>
    <Relationships>
      <Item type="Property" id="074E4827E5044F8BA6B6FD546E21D271" action="add">
        <data_type>decimal</data_type>
        <source_id keyed_name="Part" type="ItemType" name="Part">4F1AC04A2B484F3ABA4E20DB63808A88</source_id>
        <name>cost</name>
      </Item>
    </Relationships>
  </Item>
</AML>
```

`ItemType action="edit"` 配下で固有プロパティを追加する例:

```xml
<AML>
  <Item type="ItemType" id="4F1AC04A2B484F3ABA4E20DB63808A88" action="edit">
    <Relationships>
      <Item type="Property" id="879EAA0579BD4120BF3DF324ABA7A341" action="add">
        <data_type>string</data_type>
        <source_id keyed_name="Part" type="ItemType" name="Part">4F1AC04A2B484F3ABA4E20DB63808A88</source_id>
        <name>item_number</name>
      </Item>
    </Relationships>
  </Item>
</AML>
```

## 標準プロパティ候補

既存の Form チェックで使っている `STANDARD_PROPERTIES` と同じ一覧を候補として使う。

ただし、public 配下の標準パッケージ XML では `release_date` が `ItemType action="add"` 配下の `Property action="add"` として追加されている例が複数ある。

そのため、このタスクで `Property action="add"` を失敗にする対象は、public 配下で標準プロパティの上書きとして確認できた名前に限定する。少なくとも以下は `Property action="edit"` の実例が確認できる:

- `classification`
- `created_by_id`
- `created_on`
- `current_state`
- `generation`
- `locked_by_id`
- `major_rev`
- `managed_by_id`
- `modified_by_id`
- `modified_on`
- `owned_by_id`
- `state`
- `superseded_date`

`release_date` を標準プロパティとして `action="edit"` 必須にするかは、public 配下の実例と矛盾するため確認事項として残す。

## 対象

- 入力パスが `ItemType/*.xml` の AML ファイル。
- `AML/Item[@type="ItemType"]` のうち、`action="add"` または `action="edit"` の直下にある `Relationships/Item[@type="Property"]`。
- ネストした別 Item の `Relationships` 配下にある `Property` は、このチェックでは対象にしない。

## 非対象

- `Form/*.xml` の `Field` / `propertytype_id` チェック。
- Property のデータ型、ラベル、sort_order などの詳細妥当性。
- `RelationshipType/*.xml` 内に埋め込まれた relationship ItemType の `Property` 配置チェック。
- `source_id` の GUID 実在確認、`where` 条件式の完全な構文検証。
- Aras サーバー側インポートの完全な再現。

## public 配下で確認した代表例

- `public/PLM/Import/ItemType/Part.xml`
  - `cost` などの固有プロパティは `ItemType action="add"` 配下の `Property action="add"`。
  - `state` / `classification` / `major_rev` / `superseded_date` は別の `ItemType action="edit"` 配下の `Property action="edit"`。
  - `item_number` は `ItemType action="edit"` 配下でも `Property action="add"` として追加されている。
- `public/PLM/Import/ItemType/CAD.xml`
  - `created_by_id` / `created_on` / `current_state` / `generation` / `locked_by_id` / `modified_by_id` / `modified_on` などが `Property action="edit"`。
- `public/PLM/Import/ItemType/Simple ECO.xml`
  - `created_on` / `managed_by_id` / `owned_by_id` / `state` は `Property action="edit"`。
  - `release_date` は `Property action="add"`。

## テスト

- 標準プロパティが `Property action="edit"` なら成功する。
- ItemType 固有プロパティが `Property action="add"` なら成功する。
- public 配下で `action="edit"` の標準プロパティ上書きとして確認できたプロパティが `Property action="add"` なら失敗する。
- `release_date` の `Property action="add"` は、public 配下の実例と矛盾しないよう、このタスクでは失敗にしない。
- `ItemType/*.xml` 以外ではこのチェックを実行しない。
