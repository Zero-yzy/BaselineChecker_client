import datetime
from scan.Base import Base


def update_check(task_id, basename):
    result = {}
    # 编辑URL
    result["url"] = "/updateChecks/insert"
    # 获取基本信息
    data = Base.get_update_info(task_id, basename)
    # 组装发送的类型
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    result['finish_time'] = time
    result['send_data'] = data
    # print(send_data.encode('utf-8'))

    return result
