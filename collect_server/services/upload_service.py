import os
import tarfile
import json
from fastapi import HTTPException, UploadFile

async def process_upload(
    host: str,
    file: UploadFile,
    os_info: str,
    environment_variables: str,
    aliases: str,
    installed_packages: str,
) -> str:
    """
    アップロードされたシステムデータを処理し、ホスト名ごとに整理して保存します。

    Args:
        host (str): ホスト名（識別子）。
        file (UploadFile): アップロードされたtar.gzファイル。
        os_info (str): OS情報のJSON文字列。
        environment_variables (str): 環境変数のJSON文字列。
        aliases (str): シェルエイリアス情報。
        installed_packages (str): インストール済みパッケージリスト。

    Raises:
        HTTPException: JSONのデコードエラー、ファイル操作エラー、またはtar.gzファイルの展開エラー。

    Returns:
        str: 処理が成功したホスト名を含むメッセージ。
    """
    try:
        # ホスト名ごとにフォルダを作成
        host_dir = os.path.join("uploaded", host)
        os.makedirs(host_dir, exist_ok=True)

        # OS情報の保存
        try:
            os_info_data = json.loads(os_info)
            os_info_path = os.path.join(host_dir, "os_info.json")
            with open(os_info_path, "w") as f:
                json.dump(os_info_data, f, indent=4)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid OS info JSON: {e}")

        # 環境変数の保存
        try:
            env_vars_data = json.loads(environment_variables)
            env_vars_path = os.path.join(host_dir, "environment_variables.json")
            with open(env_vars_path, "w") as f:
                json.dump(env_vars_data, f, indent=4)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid environment variables JSON: {e}")

        # エイリアスの保存
        aliases_path = os.path.join(host_dir, "aliases.txt")
        with open(aliases_path, "w") as f:
            f.write(aliases)

        # インストールされているパッケージ一覧の保存
        packages_path = os.path.join(host_dir, "installed_packages.txt")
        with open(packages_path, "w") as f:
            f.write(installed_packages)

        # tar.gzファイルの保存
        tar_file_path = os.path.join(host_dir, file.filename)
        try:
            with open(tar_file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save tar.gz file: {e}")

        # tar.gzファイルの展開
        extracted_dir = os.path.join(host_dir, "extracted")
        os.makedirs(extracted_dir, exist_ok=True)
        try:
            with tarfile.open(tar_file_path, "r:gz") as tar:
                tar.extractall(path=extracted_dir)
        except tarfile.TarError as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract tar.gz file: {e}")

        # /etc/environment と /etc/profile を確認して保存
        specific_files = ["environment", "profile"]
        for file in specific_files:
            file_path = os.path.join(extracted_dir, file)
            if os.path.exists(file_path):
                dest_path = os.path.join(host_dir, f"{file}.txt")
                try:
                    with open(file_path, "r") as src, open(dest_path, "w") as dest:
                        dest.write(src.read())
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to process {file}: {e}")

        return f"Data uploaded and processed successfully for host '{host}'"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
