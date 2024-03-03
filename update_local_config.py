from notion_client import Client
import os
import shutil

# otion API 密钥和数据库 ID
notion_token = "secret_bZVRV08haYlHmwTVwWVoHSpobh2tQ8kxaicRU0VFRME"
database_id = "8e7928585c4743c09eb25ec15e267da0"

# 初始化 Notion 客户端
notion = Client(auth=notion_token)


def query_database(database_id):
    """查询 Notion 数据库并返回响应结果，按 QQ号 升序排序，同时过滤出 QQ号、平台ID 和 关键词 都不为空的页面。"""
    try:
        response = notion.databases.query(
            **{
                "database_id": database_id,
                "sorts": [{"property": "QQ号", "direction": "ascending"}],
                "filter": {
                    "and": [
                        {"property": "QQ号", "number": {"is_not_empty": True}},
                        {"property": "平台ID", "rich_text": {"is_not_empty": True}},
                        {"property": "关键词", "relation": {"is_not_empty": True}},
                    ]
                },
            }
        )
        return response["results"]
    except Exception as e:
        print(f"查询数据库时出现错误: {e}")
        return []


def create_directory(path):
    """创建目录，如果目录已存在，则先删除再创建"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def write_file(file_path, content):
    """写入文件，如果文件不存在则创建"""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def create_file_structure(pages):
    """根据 Notion 数据库中的页面信息创建文件结构"""
    for page in pages:
        properties = page["properties"]

        deploy_server = (
            properties["部署服务器"]["select"]["name"]
            if properties["部署服务器"].get("select")
            else None
        )
        qq_number = (
            str(properties["QQ号"]["number"])
            if properties["QQ号"].get("number") is not None
            else None
        )

        # 只有当部署服务器和QQ号都存在时才进行处理
        if deploy_server and qq_number:
            dir_path = os.path.join(deploy_server, qq_number)
            create_directory(dir_path)  # 创建目录

            # 文件名构造和空文件创建逻辑
            qq_name = (
                properties["QQ名"]["title"][0]["plain_text"]
                if properties["QQ名"].get("title")
                else None
            )
            platform_name = (
                properties["平台名"]["rich_text"][0]["plain_text"]
                if properties["平台名"].get("rich_text")
                else None
            )
            if qq_name and platform_name:
                file_path = os.path.join(dir_path, f"{qq_name}-{platform_name}")
                open(file_path, "w").close()  # 创建空文件

            # 写入或更新 compose.yml 和 notify.toml 文件
            compose_yml = (
                properties["compose.yml"]["formula"]["string"]
                if properties["compose.yml"].get("formula")
                else None
            )
            notify_toml = (
                properties["notify.toml"]["formula"]["string"]
                if properties["notify.toml"].get("formula")
                else None
            )
            if compose_yml:
                write_file(os.path.join(dir_path, "compose.yaml"), compose_yml)
            if notify_toml:
                write_file(os.path.join(dir_path, "notify.toml"), notify_toml)


def main():
    """主函数，执行程序的主要逻辑"""
    pages = query_database(database_id)
    if pages:
        create_file_structure(pages)
    else:
        print("未查询到页面数据。")


if __name__ == "__main__":
    main()
