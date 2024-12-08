def generate_docker_compose(host, output_file="docker-compose.yml"):
    """
    指定されたホスト名を基に、docker-compose.ymlファイルを生成します。

    Args:
        host (str): コンテナ名に使用するホスト識別子。
        output_file (str, optional): 生成されるdocker-compose.ymlファイルの出力パス。デフォルトは "docker-compose.yml"。

    Raises:
        Exception: ファイルの書き込みや処理中にエラーが発生した場合。

    Returns:
        None
    """
    try:
        docker_compose_content = f"""version: '3.8'
services:
  app:
    build:
      context: .
    container_name: dev_{host}_container
    tty: true
"""

        # docker-compose.yml ファイルを書き込む
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(docker_compose_content)

        print(f"docker-compose.yml が生成されました: {output_file}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")


# generate_docker_compose(output_file="uploaded/localhost.localdomain/docker-compose.yml")
