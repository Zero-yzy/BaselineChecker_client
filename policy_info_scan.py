import datetime
from scan.policy_check import get_policy_info


def policy_check(task_id, bsaename):
    result = {}
    # 编辑URL
    result["url"] = "/policyChecks/insert"
    # 组装发送的类型
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    result['finish_time'] = time

    # 获取基本信息
    data = get_policy_info(task_id, bsaename)
    result['send_data'] = data

    return result
