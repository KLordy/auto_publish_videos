import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

from common.conf import BASE_DIR, FEISHU_ROBOT_URL
from model.model import ShipinhaoUserInfo, get_session
from util.file_util import get_account_file
from util.request_util import HttpRequester
from util.robot_util import send_feishu_msg


async def save_storage_state(account_file: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://channels.weixin.qq.com")
        print("请在浏览器中扫码登录...")
        await asyncio.sleep(60)  # 给用户60秒时间进行扫码登录

        # 保存存储状态到文件
        storage_state = await context.storage_state()
        with open(account_file, 'w') as f:
            f.write(json.dumps(storage_state))
        await browser.close()


# async def weixin_setup(connection, handle=False, shipinhao_user_id='', shipinhao_username=''):
#     # 依据user_id来生成 cookie文件夹
#     user_ck_path = "{}_account.json".format(shipinhao_user_id)
#     account_file = Path(BASE_DIR / "cookies" / user_ck_path)
#     # account_file = get_absolute_path(account_file, "tencent_uploader")
#     # if not os.path.exists(account_file) or not await cookie_auth(account_file):
#     cookies = get_shipinhao_user_cookie(shipinhao_user_id, connection)
#     if len(cookies) > 0 and not await db_cookie_auth(cookies):
#         if not handle:
#             # Todo alert message
#             return False
#         print('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
#         requester = HttpRequester()
#         post_response = requester.post(FEISHU_ROBOT_URL, json={"user": shipinhao_username},
#                                        headers={"Content-Type": "application/json"})
#         print('robot alert response: ', post_response)
#         os.system('python3 -m playwright install')
#         os.system(f'playwright codegen channels.weixin.qq.com --save-storage={account_file}')  # 生成cookie文件
#         # await get_and_save_cookies(connection=connection, shipinhao_user_id=shipinhao_user_id)
#         await save_cookies_from_file_to_database(shipinhao_user_id)
#     return True


async def check_and_update_cookie(shipinhao_userinfo: ShipinhaoUserInfo, handle=False) -> object:
    # user_ck_path = "{}_account.json".format(shipinhao_userinfo.shipinhao_user_id)
    # account_file = Path(BASE_DIR / "cookies" / user_ck_path)
    account_file = get_account_file(shipinhao_userinfo.shipinhao_user_id)
    cookies = shipinhao_userinfo.cookies
    if len(cookies) < 10 or (len(cookies) > 10 and not await db_cookie_auth(cookies, shipinhao_user_id=shipinhao_userinfo.shipinhao_username)):
        if not handle:
            # Todo alert message
            return False
        print('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
        # requester = HttpRequester()
        # post_response = requester.post(FEISHU_ROBOT_URL, json={"user": shipinhao_userinfo.shipinhao_username},
        #                                headers={"Content-Type": "application/json"})
        post_response = send_feishu_msg(shipinhao_userinfo.shipinhao_username)
        print('robot alert response: ', post_response)
        os.system('python3 -m playwright install')
        os.system(f'playwright codegen channels.weixin.qq.com --save-storage={account_file}')  # 生成cookie文件
        await save_cookies_from_file_to_database(shipinhao_userinfo.shipinhao_user_id)
    return True


async def db_cookie_auth(cookie_data, shipinhao_user_id=''):
    if len(cookie_data) < 10 or cookie_data == '[]':  # cookie为空，或者是空数组
        return False
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        # 将cookie数据从字符串转换为字典列表（如果cookie_data已经是字典列表则不需要转换）
        cookies_obj = json.loads(cookie_data) if isinstance(cookie_data, str) else cookie_data
        context = await browser.new_context()

        # 将cookie设置到浏览器上下文中
        cookies = cookies_obj['cookies']
        await context.add_cookies(cookies)
        # 创建一个新的页面
        page = await context.new_page()

        # 设置localStorage
        origins = cookies_obj.get('origins', [])
        if origins:
            for origin in origins:
                await page.goto(origin['origin'])  # 跳转到指定的origin
                for item in origin.get('localStorage', []):
                    await page.evaluate(f"""localStorage.setItem('{item["name"]}', '{item["value"]}')""")

        # 访问指定的 URL
        await page.goto("https://channels.weixin.qq.com/platform/post/create")
        try:
            await page.wait_for_selector('div.title-name:has-text("视频号小店")', timeout=10000)  # 等待5秒
            print(f"{shipinhao_user_id} [+] 等待5秒 cookie 失效")
            return False
        except:
            print(f"{shipinhao_user_id} [+] cookie 有效")
            return True


async def save_cookies_from_file_to_database(shipinhao_user_id):
    # 依据user_id来生成 cookie文件夹
    account_file = get_account_file(shipinhao_user_id)
    # 从文件中读取cookie信息
    with open(account_file, 'r') as file:
        cookies = json.load(file)

    # 连接到数据库
    session = get_session()
    cookie_str = json.dumps(cookies)  # 将cookie转换为JSON字符串
    session.query(ShipinhaoUserInfo).filter_by(shipinhao_user_id=shipinhao_user_id).update(
        {ShipinhaoUserInfo.cookies: cookie_str})
    session.commit()
    session.close()
