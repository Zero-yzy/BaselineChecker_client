import socket
import datetime
from const.Type import Type
from scan.Base import Base


def autorun_check(task_id, basename):
    result = {}
    # 编辑URL
    result["url"] = "/autoChecks/insert"
    # 获取基本信息
    data = Base.get_autoruns(task_id, basename)
    # 组装发送的类型
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    result['finish_time'] = time
    result['send_data'] = data
    # print(send_data.encode('utf-8'))

    return result
