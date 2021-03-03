IPアドレス検索ツール
=================

## 概要
- IPアドレスよりCIDR形式のネットワークアドレス、国名コードを求める。

## 動かし方
### 動作条件
- dockerが動いていること

### 実行手順 
```
cd ${HOME}
git clone https://github.com/hidekuno/cidr-lite
cd cidr-lite/docker
docker build -t ${yourid}/cidr-lite --file=Dockerfile --build-arg token=${YOUR_TOKEN_ID} .
docker run -it --name cidr-lite ${yourid}/cidr-lite python3 /root/cidr_search.py
```
![image](https://user-images.githubusercontent.com/22115777/67066250-a798f900-f1ac-11e9-9765-861678a7d32b.png)
