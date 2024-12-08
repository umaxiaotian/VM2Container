import os
import json
import fnmatch
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
template_file="templates/dockerfile_template.j2"

def generate_dockerfile_with_jinja(
    json_file,
    packages_file,
    specific_files,
    aliases_file,
    env_vars_file,
    output_file="Dockerfile",
    exclude_list=None,
):
    try:
        # デフォルトの除外リスト
        if exclude_list is None:
            exclude_list = []

        # JSONファイルの読み込み
        with open(json_file, "r", encoding="utf-8") as f:
            os_info = json.load(f)

        # 必須情報を取得
        base_image = os_info.get("ID", "").replace("\"", "")
        version = os_info.get("VERSION_ID", "").replace("\"", "")

        if not base_image or not version:
            raise ValueError("ID または VERSION_ID が見つかりません。")

        # パッケージリストの読み込み
        with open(packages_file, "r", encoding="utf-8") as f:
            packages = [pkg for pkg in f.read().strip().splitlines() if not pkg.startswith("gpg-pubkey")]

        if not packages:
            raise ValueError("パッケージリストが空です。")

        # エイリアスの読み込み
        with open(aliases_file, "r", encoding="utf-8") as f:
            aliases = f.read().strip().splitlines()

        # 環境変数の読み込み
        with open(env_vars_file, "r", encoding="utf-8") as f:
            env_vars = json.load(f)

        # ターゲットディレクトリリスト
        target_dirs = ["etc", "bin", "opt", "sbin"]

        # Jinja2 環境をセットアップ
        env = Environment(loader=FileSystemLoader("."), trim_blocks=True, lstrip_blocks=True)

        # カスタムフィルタを追加
        env.filters["fnmatch_filter"] = lambda key, patterns: any(fnmatch.fnmatch(key, pattern) for pattern in patterns)
        env.filters["basename"] = os.path.basename

        # テンプレートを読み込む
        try:
            template = env.get_template(template_file)
        except TemplateNotFound:
            raise FileNotFoundError(f"テンプレートファイルが見つかりません: {template_file}")

        # Dockerfile をレンダリング
        dockerfile_content = template.render(
            base_image=base_image,
            version=version,
            packages=packages,
            aliases=aliases,
            env_vars=env_vars,
            target_dirs=target_dirs,
            specific_files=specific_files,
            exclude_list=exclude_list,
        )

        # Dockerfile を保存
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        print(f"Dockerfile が生成されました: {output_file}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
# # Dockerfile定義
# specific_files = ["/etc/environment", "/etc/profile"]
# # 除外する環境変数
# exclude_list = ["BASH_FUNC_which%%", "SSH*"] 
# generate_dockerfile_with_jinja(

#     json_file="uploaded/localhost.localdomain/os_info.json",
#     extracted_dir="uploaded/localhost.localdomain/extracted",
#     packages_file="uploaded/localhost.localdomain/installed_packages.txt",
#     specific_files=specific_files,
#     aliases_file="uploaded/localhost.localdomain/aliases.txt",
#     env_vars_file="uploaded/localhost.localdomain/environment_variables.json",
#     output_file="uploaded/localhost.localdomain/Dockerfile",
#     exclude_list=exclude_list
# )
