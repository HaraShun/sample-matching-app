件名：GCP通知（VPC-SC / ACM identity format変更）影響調査 報告


お疲れ様です。GCPからの通知について、調査結果をご報告します。


■ 通知の概要
Access Context Manager（ACM）の access level および VPC Service Controls（VPC-SC）の ingress/egress ルールに設定されている identity（ユーザー・サービスアカウント等）の記載形式が不正な場合、2026年9月1日以降にアクセス拒否や設定変更の失敗が発生するという内容。


■ 当環境との関連
当環境では VPC-SC を利用しているため、本件の確認対象に該当します。
（VPC-SC を利用している場合、ACM も自動的に使用されています。）


■ 確認結果
Google Cloud Console にて、以下の2箇所を確認しました。
（1）VPC Service Controls（各 service perimeter の ingress/egress ルール内の identity）
　→ 【現時点では問題ないと考えます】
　→ 理由：GUI 上、From ID は「任意の ID」となっており、個別の user: / serviceAccount: 形式の identity を列挙する設定ではありませんでした。今回の通知対象は、個別 identity の prefix が不正なケースであるため、少なくとも確認した perimeter の当該ルールについては直接の対象ではないと考えます。
　→ スクショ画像を貼る

（2）Access Context Manager（各 access level の members）
　→ 【GUI による一次確認のみでは完全判定不可】
　→ 理由：GUI ではプレフィックス部分が確認できないため、「GUI にて、編集ボタンを押下して確認」または「CLI による出力確認」が必要と考えます
　→ スクショ画像を貼る


■ ACM に不正な形式があった場合
・2026年9月1日までに修正が必要
・対応内容は、identity の prefix を正しい形式へ修正すること
  ※ Access level の members で正しい形式は user:EMAIL または serviceAccount:EMAIL
  ※ 例：serviceAccount:user@example.com → user:user@example.com
 

■ ACM 修正時の反映リードタイム

Access Context Manager の access level の members の値の修正反映リードタイムについての明言は、
公式ドキュメントでは明言されているものは見つかりませんでしたが。

近しいサービスの「コンテキストアウェア アクセスのバインディングの反映」では、

```
バインディングが反映されるまでに数分かかることがあります。
```
『 コンテキストアウェア アクセスを設定する  |  Access Context Manager  |  Google Cloud Documentation 』
(https://docs.cloud.google.com/access-context-manager/docs/securing-console-and-apis?hl=ja )

とのことなので、反映まで数分のリードタイムがかかるのではないかと推測されます。


以上です。

----------------------------------------------------------------------------------------------------------------------------------

Access Context Manager の access level に設定されている identity（members）のプレフィックスを確認するため、以下の CLI を実行させていただきたいです。

手順①：アクセスポリシーの ID を取得する

```
gcloud access-context-manager policies list --organization=<ORG_ID>
```
アクセスポリシーの名前は、gcloud コマンドラインツールで access level 関連のコマンドを実行する際に必要となります。

参考：『アクセス ポリシーを管理する | Access Context Manager | Google Cloud』
https://cloud.google.com/access-context-manager/docs/manage-access-policy


手順②：access level の一覧と詳細を出力する
```
gcloud access-context-manager levels list --policy=<POLICY_ID> --format=yaml
```
access level の一覧を取得するには list コマンドを使用します。

参考：『アクセスレベルの管理 | Access Context Manager | Google Cloud』
https://docs.cloud.google.com/access-context-manager/docs/manage-access-levels


確認観点
出力される yaml の members: フィールドに、identity が表示されます。

- 一般ユーザーのメールアドレス → user: で始まっていること
- 〇〇.iam.gserviceaccount.com → serviceAccount: で始まっていること

```
basic:
  conditions:
  - members:
    - user:taro@example.com           ← OK
    - serviceAccount:sa@proj.iam.gserviceaccount.com  ← OK
    - serviceAccount:taro@example.com  ← NG（人間なのにserviceAccount）
```


『 アクセスレベルの属性  |  Access Context Manager  |  Google Cloud Documentation 』
(https://docs.cloud.google.com/access-context-manager/docs/access-level-attributes?hl=ja#members )
