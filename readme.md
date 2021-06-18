# MyDNS.JPにIPの変更を通知する
- Linuxのcronに設定するとIPアドレスが変更した時か24時間経過したときにMyDNSにIPアドレスを登録する
- 実行間隔を短くてもMyDNSへの登録はIPが変更した場合か前回登録時から24時間経過した場合

## 実行環境
- python3.6
- 依存ライブラリなし

## 利用方法
- 以下の環境変数にMyDNSに登録しているIP,PASSWORDを登録する
    - mydns_id, mydns_pass
- crontabでmydns_update.pyを任意の間隔で実行されるように登録を行う


## 環境変数の登録
- mydns_env.shに環境変数の定義を追加する

```
export mydns_id=<your id>
export mydns_pass=<your password>
```

## 1分に一回実行する場合
```
*/1 * * * * source ~/mydns_update/mydns_env.sh && /usr/bin/python3 ~/mydns_update/mydns_update.py
```
