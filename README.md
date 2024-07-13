# Expand_Urls

Discordにて送信されたメッセージURLを展開し、Ephemeralで展開したメッセージを表示します。

## 展開のやり方
1. メッセージを長押し/メッセージを右クリック
2. アプリから「メッセージURLを展開する」を押す
<img src="https://i.imgur.com/EEaeQQd.png" width="311" height="331">

展開したメッセージは以下の表記で表示されます。
- 送信されたサーバーの名前
- チャンネル
- 送信者
- 送信者のアイコン
- 送信時間
- メッセージ内容

<img src="https://i.imgur.com/x1Ze3Hx.png" width="487" height="272">

また、画像・埋め込みがある場合は
「`このメッセージには画像/埋め込みが存在しています。
画像/埋め込みを表示する場合は下のボタンを押してください。`」と表示されます。

<img src="https://i.imgur.com/IMfhktZ.png" width="324" height="236">

### もしURLが複数ある場合
メッセージ内で**一番上にある**リンクのメッセージを表示し、そのほかのURLの展開はセレクトを用いて表示することが可能です。
セレクトのレーベルは「`送信されたチャンネル名`での発言」になります。
> [!NOTE]
> メッセージ内にURLが27個以上ある場合は27個以降のURLはセレクトの追加できる数の制限の影響で展開ができません。

<img src="https://i.imgur.com/dXJp4YE.png" width="407" height="146">

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
