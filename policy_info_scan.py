import socket
import datetime
from const.Type import Type
from scan.Base import Base
from scan.policy_check import get_policy_info
import ctypes
import sys


# 获取管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()

    except:
        return False


def policy_check(task_id, bsaename):
    result = {}
    # 编辑URL
    result["url"] = "/policyChecks/insert"
    # 组装发送的类型
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    result['finish_time'] = time

    if is_admin():
        # 获取基本信息
        data = get_policy_info(task_id, bsaename)
        result['send_data'] = data
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

    print(result)
    return result
