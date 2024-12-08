from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.upload_service import process_upload
from services.generate_dockerfile_with_dirs import (
    generate_dockerfile_with_jinja,
)
from services.generate_docker_compose import (
    generate_docker_compose,
)
app = FastAPI()

# アクセストークン
ACCESS_TOKEN = "TEST_ACCESS_TOKEN"
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    アクセストークンを検証します。

    Args:
        credentials (HTTPAuthorizationCredentials): リクエストから提供された認証情報。

    Raises:
        HTTPException: アクセストークンが無効な場合。

    Returns:
        None
    """
    if credentials.credentials != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="無効なアクセストークンです")


@app.post("/api/upload", dependencies=[Depends(verify_token)])
async def upload_system_data(
    host: str = Form(...),
    file: UploadFile = File(...),
    os_info: str = Form(...),
    environment_variables: str = Form(...),
    aliases: str = Form(...),
    installed_packages: str = Form(...),
):
    """
    システムデータをアップロードし、必要なDockerfileとdocker-composeファイルを生成します。

    Args:
        host (str): アップロード対象ホストの識別子。
        file (UploadFile): アップロードされたファイル。
        os_info (str): OSに関する情報。
        environment_variables (str): 環境変数データ。
        aliases (str): エイリアスデータ。
        installed_packages (str): インストールされているパッケージのデータ。

    Raises:
        HTTPException: 処理中にエラーが発生した場合。

    Returns:
        dict: 成功時のメッセージ。
    """
    try:
        # 送信されたデータを格納
        message = await process_upload(
            host=host,
            file=file,
            os_info=os_info,
            environment_variables=environment_variables,
            aliases=aliases,
            installed_packages=installed_packages,
        )
        print(message)

        # Dockerfile定義
        specific_files = ["/etc/environment", "/etc/profile"]
        # 除外する環境変数
        exclude_list = ["BASH_FUNC_which%%", "SSH*"] 
        # Dockerfileを作成
        generate_dockerfile_with_jinja(
            json_file=f"uploaded/{host}/os_info.json",
            packages_file=f"uploaded/{host}/installed_packages.txt",
            specific_files=specific_files,
            aliases_file=f"uploaded/{host}/aliases.txt",
            env_vars_file=f"uploaded/{host}/environment_variables.json",
            output_file=f"uploaded/{host}/Dockerfile",
            exclude_list=exclude_list,
        )
        
        generate_docker_compose(host, f"uploaded/{host}/docker-compose.yml")
        return {"message": "OK!"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"エラーが発生しました: {e}"
        )
