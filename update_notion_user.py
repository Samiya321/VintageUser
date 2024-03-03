import requests
import os
from notion_client import Client
import json

# 初始化 Notion 客户端
notion = Client(auth="secret_bZVRV08haYlHmwTVwWVoHSpobh2tQ8kxaicRU0VFRME")
database_id = "8e7928585c4743c09eb25ec15e267da0"
qqqun_number = "217518829"

# 读取 cookies
def load_cookies_from_file(file_path="cookies.json"):
    if not os.path.exists(file_path):
        print("Cookie 文件不存在，请运行 cookie.py 来获取新的 cookies。")
        return None
    with open(file_path, "r") as file:
        return json.load(file)


# bkn 计算函数
def bkn(skey):
    t = 5381
    for ch in skey:
        t += (t << 5) + ord(ch)
    return t & 2147483647


# 获取QQ群成员列表
def fetch_qq_group_members(cookies, qqqun_number):
    members = {}
    st = 0  # 起始位置
    batch_size = 40  # 每次请求获取的成员数量

    while True:
        # 更新请求参数中的st和end，以获取不同范围的成员
        data = {
            "gc": qqqun_number,
            "st": st,
            "end": st + batch_size,
            "sort": "0",
            "bkn": bkn(cookies.get("skey", "")),
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "; ".join([f"{name}={value}" for name, value in cookies.items()]),
            "User-Agent": "Mozilla/5.0",
        }
        url = "https://qun.qq.com/cgi-bin/qun_mgr/search_group_members"
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            json_response = response.json()
            if json_response.get("ec") == 0:
                # 合并当前批次获取的成员到总列表中
                batch_members = {
                    member["uin"]: member["nick"]
                    for member in json_response.get("mems", [])
                }
                members.update(batch_members)

                # 如果已获取所有成员，则退出循环
                if len(members) >= json_response.get("count", 0):
                    break

                # 准备下一批次请求
                st += batch_size + 1
            else:
                print("请求失败，可能是因为 cookies 失效。")
                break
        else:
            print(f"请求失败，状态码: {response.status_code}")
            break

    return members


def sync_notion_database(members):
    if not members:
        print("没有成员数据，同步操作终止。")
        return

    # 获取数据库当前条目
    database_items = notion.databases.query(database_id=database_id)["results"]

    # 将数据库条目转换为 {QQ号: (QQ名, page_id)} 的映射
    database_mapping = {}
    for item in database_items:
        properties = item["properties"]
        qq_number_prop = properties.get("QQ号", {}).get("number")
        qq_name_prop = (
            properties.get("QQ名", {}).get("title", [{}])[0].get("plain_text", "")
        )
        if qq_number_prop is not None:
            database_mapping[str(qq_number_prop)] = (qq_name_prop, item["id"])

    # 对比并更新 Notion 数据库
    updated_members = set()
    for uin, nick in members.items():
        uin_str = str(uin)
        if uin_str in database_mapping:
            # 如果 QQ 名不匹配，则更新
            if database_mapping[uin_str][0] != nick:
                notion.pages.update(
                    page_id=database_mapping[uin_str][1],
                    properties={"QQ名": {"title": [{"text": {"content": nick}}]}},
                )
        else:
            # 如果成员在 Notion 数据库中不存在，则添加
            notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "QQ名": {"title": [{"text": {"content": nick}}]},
                    "QQ号": {"number": int(uin)},
                },
            )
        updated_members.add(uin_str)

    # 检查并删除 Notion 数据库中已不存在的成员
    for uin, (_, page_id) in database_mapping.items():
        if uin not in updated_members:
            notion.pages.update(page_id=page_id, archived=True)


if __name__ == "__main__":
    cookies = load_cookies_from_file()
    if cookies:
        members = fetch_qq_group_members(cookies, qqqun_number)
        if members:
            sync_notion_database(members)
        else:
            print("获取 QQ 群成员信息失败。")
    else:
        print("无法加载 cookies。")
