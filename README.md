# VHDtoContainer
サンプルです。

# Serverを動かす
サーバーフォルダへ移動
```
cd collect_server
```
Pythonの仮想環境の立ち上げ
```
python -m venv venv
```
必要なパッケージを入れる
```
pip install -r requirements.txt
```
自分のローカルIPをチェック(Agentでの送り先の指定に使います）
- Windows
  ```
  ipconfig
  ```
- Linux
  ```
  ip addr
  ```

サーバーを起動
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

# ローカルエージェントを動かして収集したものを送る
エージェントファイルに移動
```
cd collect_agent
```

エージェントファイルのSERVER_URLのIPを上記でローカルIPをチェックしたものに置き換える
```
# イメージなのであなたの環境に合わせてください
SERVER_URL = "http://192.168.11.27:8000/api/upload"  -> SERVER_URL = "http://192.168.31.100:8000/api/upload" 
```

sudoは/usr/binなどを探索するのに必要です。
```
sudo python agent.py
```

サーバー側の`collect_server`内に`uploaded`ができたと思います。その中にDockerイメージをビルドするためのファイルをエクスポートしているので、`docker-compose build`してイメージをビルドした後に使ってみてください
