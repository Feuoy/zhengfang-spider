import time
import requests
import json
from db.model import t_tm_leave, t_tm_attendance


def getTm(studentnumber, password):
    account_data = {
        "username": studentnumber,
        "password": password
    }
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host': 'tm.bnuz.edu.cn',
        'Referer': 'http://tm.bnuz.edu.cn/ui/login',
        'X-Requested-With': 'XMLHttpRequest',
        "Cookie": "",
        "Connection": "keep-alive",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }
    session = requests.session()
    second = session.get("http://tm.bnuz.edu.cn/login", headers=headers, allow_redirects=False)
    xsrf = second.headers.get("Set-Cookie")[11:47]
    jessionid = second.headers.get("Set-Cookie")[68:100]
    headers['Cookie'] = "XSRF-TOKEN=" + xsrf + "; JSESSIONID=" + jessionid
    third = session.get(second.headers.get("Location"), headers=headers, allow_redirects=False)
    uaa = third.headers.get("Set-Cookie")[15:51]
    headers['Cookie'] = "UAA-XSRF-TOKEN=" + uaa + "; XSRF-TOKEN=" + xsrf + "; JSESSIONID=" + jessionid
    headers['X-UAA-XSRF-TOKEN'] = uaa
    headers['X-XSRF-TOKEN'] = xsrf
    five = session.post(third.headers.get("Location"), headers=headers, data=account_data, allow_redirects=False)
    if five.headers.get("Location") == 'http://tm.bnuz.edu.cn/uaa/login?error':
        return 4001
    nuaa = five.headers.get("Set-Cookie")[93:129]
    njess = five.headers.get("Set-Cookie")[153:185]
    headers[
        'Cookie'] = "JSESSIONID=" + njess + "; JSESSIONID=" + jessionid + "; UAA-XSRF-TOKEN=" + nuaa + "; XSRF-TOKEN=" + xsrf
    six = session.get(five.headers.get("Location"), headers=headers, allow_redirects=False)
    seven = session.get(six.headers.get("Location"), headers=headers, allow_redirects=False)
    eight = session.get(seven.headers.get("Location"), headers=headers, allow_redirects=False)
    night = session.get(eight.headers.get("Location"), headers=headers, allow_redirects=False)
    headers.pop("X-XSRF-TOKEN")
    headers['Cookie'] = "JSESSIONID=" + night.headers.get("Set-Cookie")[11:43] + "; XSRF-TOKEN=" + night.headers.get(
        "Set-Cookie")[145:181]
    user = session.get("http://tm.bnuz.edu.cn/api/user", headers=headers, allow_redirects=False)
    leave_url = "http://tm.bnuz.edu.cn/api/here/students/" + str(studentnumber) + "/leaves?offset=0&max=100000"
    leave = session.get(leave_url, headers=headers, allow_redirects=False)
    leave_oj = json.loads(leave.content.decode("utf-8"))
    while True:
        isExist = t_tm_leave.get_or_none(t_tm_leave.studentNumber == studentnumber)
        if isExist:
            s = t_tm_leave.get(t_tm_leave.studentNumber == studentnumber)
            s.delete_instance()
        else:
            break
    for each in leave_oj:
        single = t_tm_leave(
            studentNumber=studentnumber,
            leave_id=each['id'],
            type=each['type'],
            reason=each['reason'],
            status=each['status'],
            dateCreated=each['dateCreated'],
        )
        single.save(force_insert=True)
    attendance_url = "http://tm.bnuz.edu.cn/api/here/students/" + str(studentnumber) + "/attendances"
    attendance = session.get(attendance_url, headers=headers, allow_redirects=False)
    attendance_oj = json.loads(attendance.content.decode("utf-8"))
    while True:
        isExist = t_tm_attendance.get_or_none(t_tm_attendance.studentNumber == studentnumber)
        if isExist:
            s = t_tm_attendance.get(t_tm_attendance.studentNumber == studentnumber)
            s.delete_instance()
        else:
            break
    for each in attendance_oj["rollcalls"]:
        single = t_tm_attendance(
            studentNumber=studentnumber,
            attendance_id=each['id'],
            course=each['course'],
            courseItem=each['courseItem'],
            teacher=each['teacher'],
            week=each['week'],
            dayOfWeek=each['dayOfWeek'],
            startSection=each['startSection'],
            totalSection=each['totalSection'],
            type=each['type'],
            version=each['version'],
            freeListenFormId=each['freeListenFormId'],
            studentLeaveFormId=each['studentLeaveFormId'],
        )
        single.save(force_insert=True)
    tm_result = {
        "code": "200",
        "leave": leave_oj,
        "attendance": attendance_oj
    }
    return tm_result


def go(studentnumber, password):
    start = time.clock()
    print("studentnumber：" + studentnumber)
    tm = getTm(studentnumber, password)
    end = time.clock()
    print(end - start)
    return tm
