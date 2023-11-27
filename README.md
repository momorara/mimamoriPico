# mimamoriPico

<h4><<概要>></h4>
Raspberry Pi picoWを使った見守り機能基板のためのプログラムです。<br>
人感センサーにより人を感知して、ambientへのデータを投げてのダッシュボード表示などを行います。<br>
さらにAHT10を使用して気温、湿度を測定します。<br>
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

<h4><<動作環境>></h4>
2023/8/1 ファームウェア(micropython-firmware-pico-w-130623.uf2)　で動作確認<br>

<h4><<使用説明資料>></h4>
説明書類の中の資料を確認ください。<br>
お問い合わせに関しては、購入ページからお願いします。　<br>

<h4><<メンテナンス情報>></h4> 
基本的に基板購入者のみ使用できます。 使用に関してのトラブル・不具合に関しては責任を負いかねます。 ただし、報告していただければ、可能な範囲で改修対応いたします。<br>
資料は、説明文書・図面フォルダにあります。<br>
