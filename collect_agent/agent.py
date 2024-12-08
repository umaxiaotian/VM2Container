import os
import tarfile
import requests
import subprocess
import json
import socket

# FastAPI URLとアクセストークン
SERVER_URL = "http://192.168.11.27:8000/api/upload" #ホスト側のエンドポイントを指定します。
ACCESS_TOKEN = "TEST_ACCESS_TOKEN"

# ディレクトリ一覧
APP_DIRS = ["/usr/bin", "/usr/sbin", "/opt", "/etc"]

# 特定ファイル一覧
SPECIFIC_FILES = ["/etc/environment", "/etc/profile"]
TAR_FILE = "system_data.tar.gz"

def get_host_name():
    """ホスト名を取得する"""
    try:
        return socket.gethostname()
    except Exception as e:
        print(f"ホスト名の取得に失敗しました: {e}")
        return "unknown_host"

def get_os_info():
    """OS情報を取得する"""
    try:
        with open("/etc/os-release") as f:
            return dict(line.strip().split("=", 1) for line in f if "=" in line)
    except Exception as e:
        print(f"OS情報の取得に失敗しました: {e}")
        return {}

def get_environment_variables():
    """環境変数を取得する"""
    try:
        return dict(os.environ)
    except Exception as e:
        print(f"環境変数の取得に失敗しました: {e}")
        return {}

def get_aliases():
    """エイリアスを取得する"""
    try:
        result = subprocess.run("alias", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"エイリアスの取得に失敗しました: {result.stderr}")
            return ""
    except Exception as e:
        print(f"エイリアスの取得に失敗しました: {e}")
        return ""

def get_installed_packages():
    """インストールされているパッケージ一覧を取得する"""
    try:
        # RHEL系
        if os.path.exists("/etc/redhat-release"):
            result = subprocess.run("rpm -qa", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Debian系
        elif os.path.exists("/etc/debian_version"):
            result = subprocess.run("dpkg --get-selections", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            print("パッケージ一覧を取得できないディストリビューションです。")
            return ""

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"パッケージ一覧の取得に失敗しました: {result.stderr}")
            return ""
    except Exception as e:
        print(f"パッケージ一覧の取得に失敗しました: {e}")
        return ""

def create_tar_file(directories, specific_files, tar_file):
    """指定したディレクトリとファイルをtar.gz形式でアーカイブ"""
    try:
        with tarfile.open(tar_file, "w:gz") as tar:
            # ディレクトリを追加
            for directory in directories:
                if os.path.exists(directory):
                    print(f"ディレクトリをアーカイブに追加中: {directory}")
                    tar.add(directory, arcname=os.path.basename(directory))
                else:
                    print(f"ディレクトリが見つかりません: {directory}")

            # 特定ファイルを追加
            for file in specific_files:
                if os.path.exists(file):
                    print(f"ファイルをアーカイブに追加中: {file}")
                    tar.add(file, arcname=os.path.basename(file))
                else:
                    print(f"ファイルが見つかりません: {file}")

        print(f"アーカイブが作成されました: {tar_file}")
    except Exception as e:
        print(f"アーカイブの作成に失敗しました: {e}")

def upload_data(host, tar_file, os_info, env_vars, aliases, packages):
    """tarファイルとその他の情報をFastAPIサーバーにアップロード"""
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    files = {"file": open(tar_file, "rb")}
    data = {
        "os_info": json.dumps(os_info),
        "environment_variables": json.dumps(env_vars),
        "aliases": aliases,
        "installed_packages": packages,
        "host": host,  # ホスト名を送信
    }

    try:
        response = requests.post(SERVER_URL, files=files, data=data, headers=headers)
        response.raise_for_status()
        print("データが正常にアップロードされました。")
    except requests.exceptions.RequestException as e:
        print(f"データのアップロードに失敗しました: {e}")

if __name__ == "__main__":
    host_name = get_host_name()
    os_info = get_os_info()
    environment_variables = get_environment_variables()
    aliases = get_aliases()
    installed_packages = get_installed_packages()

    # 必要なディレクトリと特定ファイルをtar.gzに圧縮
    create_tar_file(APP_DIRS, SPECIFIC_FILES, TAR_FILE)

    # データをアップロード
    upload_data(host_name, TAR_FILE, os_info, environment_variables, aliases, installed_packages)
