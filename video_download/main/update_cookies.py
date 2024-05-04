from ctypes import Array

from model.model import ShipinhaoUserInfo, get_session
from util.cookie_util import check_and_update_cookie


def update_cookie():
    session = get_session()
    # 检查cookie并对过期cookie进行更新
    shipinhao_user_info: Array[ShipinhaoUserInfo] = session.query(ShipinhaoUserInfo).filter_by(machine_seq=1).all()
    for shipinhao_info in shipinhao_user_info:
        cookies = shipinhao_info.cookies
        check_and_update_cookie(shipinhao_info, handle=True)


if __name__ == '__main__':
    handle = False
    if not handle:
        print('as java true')
    else:
        print('as java false')
