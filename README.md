IPアドレス検索ツール
=================

## 概要
- IPアドレスよりCIDR形式のネットワークアドレス、国名コードを求める。

## 開発環境
| Item   | Ver. |
|--------|--------|
| OS     | CentOS7 |
| DB     | sqlite3 |
| Lang   | Python3.7|

## 動かし方
### 動作条件
- dockerが動いていること

```
docker pull hidekuno/cidr-lite
docker run -it --name cidr-lite hidekuno/cidr-lite python3 /root/cidr_search.py
```
![image](https://user-images.githubusercontent.com/22115777/67066250-a798f900-f1ac-11e9-9765-861678a7d32b.png)
