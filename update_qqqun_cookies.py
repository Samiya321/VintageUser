from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import json


def save_cookies_to_file(file_path="cookies.json"):
    # 指定 Edge WebDriver 的路径
    edge_driver_path = r".\msedgedriver.exe"

    # 配置 WebDriver 选项
    edge_options = Options()

    # 初始化 WebDriver 服务
    service = Service(executable_path=edge_driver_path)

    # 创建 Edge 浏览器实例
    browser = webdriver.Edge(service=service, options=edge_options)

    # 打开网站
    browser.get("https://qun.qq.com/#/login")

    # 等待用户扫码登录
    input("请扫码登录，登录成功后按回车继续...")

    # 获取并筛选 cookies
    cookies = browser.get_cookies()
    filtered_cookies = {
        cookie["name"]: cookie["value"]
        for cookie in cookies
        if cookie["name"] in ["p_skey", "p_uin", "skey"]
    }

    # 持久化保存到 JSON 文件
    with open(file_path, "w") as file:
        json.dump(filtered_cookies, file)

    # 关闭浏览器
    browser.quit()

    print(f"Cookies 已保存至 {file_path}")


if __name__ == "__main__":
    save_cookies_to_file()
