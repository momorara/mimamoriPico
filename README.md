# mimamoriPico

<h4><<概要>></h4>
Raspberry Pi picoWを使った見守り機能基板のためのプログラムです。<br>
人感センサーにより人を感知して、ambientへのデータを投げてのダッシュボード表示などを行います。<br>
さらにAHTx0を使用して気温、湿度を測定します。<br>
気温、湿度から簡易的にＷＢＧＴをを計算して表示します。<br>
Cdsセンサーも搭載して、明暗度も測定できます。<br>

それらのデータはwifiを使いambientという計測値表示サービスに投げていますので、表示データ保存が可能となっています。<br>
*参考サイト==>https://ambidata.io/bd/board.html?id=64823 <br>
これらは、基本無料サービスの範囲で使用できるものであり、 見守り機能を無料で実現できます。 ただし、通信についてはwifiを利用する必要があります。<br>
また、これらサービスを無料で使うためにそれぞれのサービスにご自身で 登録する必要があります。<br>
　・LEDの色等指定はできません。<br>
　・部品の仕様が変わる場合があります。 <br>
　・基板のバージョンが変わる場合がありますが、機能等に違いはありません。<br>

<h4><<使用方法>></h4>
git clone https://github.com/momorara/mimamoriPico<br>
でパソコンにダウンロードしてください。<br>
インストールについては、インストール文書に従いインストールを行ってください。<br>
  
 用途としては、<br>
・ひとり親の簡易見守り<br>
・子供の簡易見守り<br>
・無人建物の簡易監視<br>
・ペットの簡易見守り<br>
が考えられます。<br>

<h4><<動作環境>></h4>
2023/8/1 ファームウェア(micropython-firmware-pico-w-130623.uf2)　で動作確認<br>
2024/1/25 ファームウェア(RPI_PICO_W-20240105-v1.22.1.uf2)　で動作確認<br>
2024/7/28 ファームウェア(RPI_PICO_W-20240602-v1.23.0.uf2)　で動作確認<br>
2024/10/28 ファームウェア(RPI_PICO_W-20241025-v1.24.0.uf2)　で動作確認<br>

<h4><<使用説明資料>></h4>
説明書類の中の資料を確認ください。<br>
お問い合わせに関しては、購入ページからお願いします。　<br>

<h4><<メンテナンス情報>></h4> 
基本的に基板購入者のみ使用できます。 使用に関してのトラブル・不具合に関しては責任を負いかねます。 ただし、報告していただければ、可能な範囲で改修対応いたします。<br>
資料は、説明文書・図面フォルダにあります。<br>
2024/08/24   mqttとNode-REDダッシュボードの勧め　をアップ<br>
2024/09/02 オプションとして、LINEへのメッセージ送信ライブラリを追加しました。LINEへの通知を考えておられる方は参考にして下さい。ただし、トークンの取得はネットで調べて下さい。<br>
2024/10/27   「LINE Notify提供終了」がLINEで発表されています。https://notify-bot.line.me/closing-announce<br>
2024/11/27  夜間にLEDを点灯させない設定を追加しました。プログラムの入れ替えの場合は、一旦picoW上のプログラムを削除してから再度アップロードする必要があるかもしれません。
  
<h4><<サポート窓口>></h4>
  メールアドレスが　tkj-works@mbr.nifty.com に変更になっています。<br>
  資料等を修正中ですが、ご注意ください。<br>


