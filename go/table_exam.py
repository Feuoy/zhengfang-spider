import time
from lxml import html
etree = html.etree
import requests
import importlib, sys
from util import identifyRandcode
from db.model import t_unsuccessful_list, t_es_exam
import re
import pandas as pd
import os
from bs4 import BeautifulSoup


class student():
    studentName = ''
    header = {'User-Agent': 'Mozilla/5.0',
              'Accept-Encoding': 'gzip,deflate',
              'Connection': 'keep-alive',
              'Referer': 'http://es.bnuz.edu.cn/default2.aspx'
              }
    s = requests.session()

    def __init__(self, studentNumber, password):
        self.studentNumber = studentNumber
        self.password = password

    def getCheckCodeImage(self):
        importlib.reload(sys)
        imgUrl = "http://es.bnuz.edu.cn/CheckCode.aspx"
        imgresponse = self.s.get(imgUrl, headers=self.header)
        image = imgresponse.content
        imgresponse.close()
        DstDir = os.getcwd() + "\\"
        try:
            with open("image/original_img.jpg", "wb") as jpg:
                jpg.write(image)
        except IOError:
            print("IO Error\n")
        finally:
            jpg.close

    def login(self, checkCode):
        url = "http://es.bnuz.edu.cn/default2.aspx"
        response = self.s.get(url, headers=self.header)
        selector = etree.HTML(response.content)
        __VIEWSTATE = selector.xpath('/html/body/form[@id="form1"]/div/input/@value')[2]
        __VIEWSTATEGENERATOR = selector.xpath('/html/body/form[@id="form1"]/div/input/@value')[3]
        __PREVIOUSPAGE = selector.xpath('/html/body/form[@id="form1"]/div/input/@value')[4]
        __EVENTVALIDATION = selector.xpath('/html/body/form[@id="form1"]/div/input/@value')[5]
        RadioButtonList1 = u"学生".encode('gb2312', 'replace')
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "__PREVIOUSPAGE": __PREVIOUSPAGE,
            "__EVENTVALIDATION": __EVENTVALIDATION,
            "TextBox1": self.studentNumber,
            "TextBox2": self.password,
            "TextBox3": checkCode,
            "RadioButtonList1": RadioButtonList1,
            "Button4_test": "",
        }
        response = self.s.post(url, data=data, headers=self.header)
        content = response.content.decode('utf-8')
        selector = etree.HTML(content)
        infor = selector.xpath('//*[@id="xhxm"]/text()')[0]
        text = infor
        text = text.replace(" ", "")
        studentnumber = text[:10]
        studentname = text[10:].replace("同学", "")
        print("studentname：" + studentname)
        self.studentName = studentname
        print("studentnumber：" + studentnumber)

    def login_out(self):
        url = "http://es.bnuz.edu.cn/xs_main.aspx?xh=" + self.studentNumber
        headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }
        index = self.s.get(url, headers=headers)
        soup = BeautifulSoup(index.content, 'html5lib')
        __VIEWSTATE = soup.find('input', id='__VIEWSTATE')['value']
        __VIEWSTATEGENERATOR = soup.find('input', id='__VIEWSTATEGENERATOR')['value']
        __EVENTVALIDATION = soup.find('input', id='__EVENTVALIDATION')['value']
        data = {
            "__EVENTTARGET": "aTc2",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "__EVENTVALIDATION": __EVENTVALIDATION,
        }
        response = self.s.post(url, data=data, headers=headers)
        print(str(self.studentNumber) + " - " + str(self.studentName) + "，login out ssuccessfull")

    def getExam(self, studentNumber):
        exam_url = "http://es.bnuz.edu.cn/jwgl/xskscx.aspx?xh=" + str(self.studentNumber) + "&xm=" + str(
            self.studentName) + "&gnmkdm=N121604"
        refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        header = {
            'Referer': refer,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip,deflate'
        }
        response = self.s.get(exam_url, headers=header)
        soup = BeautifulSoup(response.content, "lxml")
        pre = soup.find(id="__VIEWSTATE")
        __VIEWSTATE = (re.findall(r'value="(.*)"', str(pre)))[0]
        ddl_xn_pre = soup.find(id="ccd_xn_ClientState")
        ddl_xn = (re.findall(r'value="(.*)"', str(ddl_xn_pre)))[0]
        ddl_xq_pre = soup.find(id="ccd_xq_ClientState")
        ddl_xq = (re.findall(r'value="(.*)"', str(ddl_xq_pre)))[0]
        formdata = {
            "ScriptManager1": "ScriptManager1|bt_kscx",
            "__VIEWSTATEENCRYPTED": "",
            "__ASYNCPOST": "true",
            "bt_kscx": "考试查询",
            "__VIEWSTATE": __VIEWSTATE,
            "ccd_xn_ClientState": str(ddl_xn + ":::" + ddl_xn),
            "ccd_xq_ClientState": str(ddl_xq + ":::" + ddl_xq),
            "ddl_xn": ddl_xn,
            "ddl_xq": ddl_xq,
        }
        headers = {
            "Referer": refer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }
        response = self.s.post(exam_url, headers=headers, data=formdata)
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(content, "lxml")
        examTimeOrCourseTime_list = []
        classroom_list = []
        try:
            for i in range(2, 20):
                if i < 10:
                    time_pre = soup.find(id="gv_ks_ctl" + "0" + str(i) + "_Label1")
                    time = (re.findall(r'_Label1">(.*)</span>', str(time_pre)))
                    room_pre = soup.find(id="gv_ks_ctl" + "0" + str(i) + "_Label2")
                    room = (re.findall(r'_Label2">(.*)</span>', str(room_pre)))
                else:
                    time_pre = soup.find(id="gv_ks_ctl" + str(i) + "_Label1")
                    time = (re.findall(r'_Label1">(.*)</span>', str(time_pre)))
                    room_pre = soup.find(id="gv_ks_ctl" + str(i) + "_Label2")
                    room = (re.findall(r'_Label2">(.*)</span>', str(room_pre)))
                examTimeOrCourseTime_list.append(str(time)[2:-2])
                classroom_list.append(str(room)[2:-2])
        except AttributeError:
            pass
        time_list = []
        examTimeOrCourseTime_list_true = []
        for i, one in enumerate(examTimeOrCourseTime_list):
            if one != '':
                if one[0] != '*':
                    time_list.append(i)
                else:
                    examTimeOrCourseTime_list_true.append(one)
        examTimeOrCourseTime_list_true.reverse()
        classroom_list_true = []
        for j, one in enumerate(classroom_list):
            if len(time_list) == 0:
                if one != '':
                    classroom_list_true.append(one)
            else:
                if j in time_list:
                    continue
                else:
                    if one != '':
                        classroom_list_true.append(one)
        classroom_list_true.reverse()
        try:
            trs = soup.find(id="gv_ks").findAll("tr")[1:]
        except AttributeError:
            return []
        Exam_list = []
        for tr in trs:
            tds = tr.findAll("td")
            oneExamKeys = [
                "examIndex",
                "classSetDepartment",
                "electiveCourseNumber",
                "courseName",
                "startWeek",
                "endWeek",
                "examTimeOrCourseTime",
                "classroom",
                "seatNumber",
                "remark",
                "slowExamination"
            ]
            oneExamValues = []
            for td in tds:
                if td.string == "\xa0":
                    td.string = ''
                oneExamValues.append(td.string)
            oneExam = {}
            oneExam["studentNumber"] = studentNumber
            oneExam_temp = dict((key, value) for key, value in zip(oneExamKeys, oneExamValues))
            oneExam.update(oneExam_temp)
            if oneExam["seatNumber"] == "未排座位":
                continue
            Exam_list.append(oneExam)
        for col in Exam_list:
            col["classroom"] = classroom_list_true.pop()
            col["examTimeOrCourseTime"] = examTimeOrCourseTime_list_true.pop()
            time_str = str(col["examTimeOrCourseTime"])
            year = time_str[1:5]
            month = time_str.split("年")[1].split("月")[0]
            day = time_str.split("年")[1].split("月")[1].split("日")[0]
            hour = time_str.split("(")[1][0:2]
            minute = time_str.split(":")[1][0:2]
            exam_start_time = year + "年" + month + "月" + day + "日" + hour + ":" + minute
            col["examTimeOrCourseTime"] = exam_start_time
        while True:
            isExist = t_es_exam.get_or_none(t_es_exam.studentNumber == str(self.studentNumber))
            if isExist:
                s = t_es_exam.get(t_es_exam.studentNumber == str(self.studentNumber))
                s.delete_instance()
            else:
                break
        for each in Exam_list:
            single = t_es_exam(
                studentNumber=str(self.studentNumber),
                examIndex=each['examIndex'],
                classSetDepartment=each['classSetDepartment'],
                electiveCourseNumber=each['electiveCourseNumber'],
                courseName=each['courseName'],
                startWeek=each['startWeek'],
                endWeek=each['endWeek'],
                examTimeOrCourseTime=each['examTimeOrCourseTime'],
                classroom=each['classroom'],
                seatNumber=each['seatNumber'],
                remark=each['remark'],
                slowExamination=each['slowExamination'],
            )
            single.save(force_insert=True)
        return Exam_list


def go(studentNumber, studentPassword):
    start = time.clock()
    unsuccessful_list = pd.DataFrame(data=[])
    i = 0
    while i < 1:
        if 1:
            print()
            print('No.' + str(i))
            try:
                current_student = student(studentNumber, studentPassword)
                current_student.getCheckCodeImage()
                orginalCheckCode = identifyRandcode.identify_randcode(
                    'image/original_img.jpg',
                    'image/adjusted_img.jpg')
                checkCode = orginalCheckCode[0:5]
                current_student.login(checkCode)
            except IndexError:
                time.sleep(1)
                print('——PasswordOrRandcode Error——Again, KillRandcode——')
                try:
                    current_student = student(studentNumber, studentPassword)
                    current_student.getCheckCodeImage()
                    orginalCheckCode = identifyRandcode.identify_randcode(
                        'image/original_img.jpg',
                        'image/adjusted_img.jpg')
                    checkCode = orginalCheckCode[0:5]
                    current_student.login(checkCode)
                except IndexError:
                    time.sleep(1)
                    reason = 'wrong password'
                    print(reason)
                    if reason == 'wrong password':
                        return 4001
                    error_info = t_unsuccessful_list(serialNumber=i, studentNumber=studentNumber,
                                                     studentPassword=studentPassword, reason=reason)
                    error_info.save()
                else:
                    print("login successfully！")
                    try:
                        Exam_list = current_student.getExam(studentNumber)
                    except IndexError:
                        reason = 'outside school'
                        print(reason)
                        error_info = t_unsuccessful_list(serialNumber=i, studentNumber=studentNumber,
                                                         studentPassword=studentPassword, reason=reason)
                        error_info.save()
                    else:
                        current_student.login_out()
                        print("successfully！")
            else:
                print("login successfully！")
                try:
                    Exam_list = current_student.getExam(studentNumber)
                except IndexError:
                    reason = 'outside school'
                    print(reason)
                    error_info = t_unsuccessful_list(serialNumber=i, studentNumber=studentNumber,
                                                     studentPassword=studentPassword, reason=reason)
                    error_info.save()
                else:
                    current_student.login_out()
                    print("successfully！")
        else:
            pass
        i = i + 1
    end = time.clock()
    print(end - start)
    t_exam = dict(
        {
            'exam': Exam_list
        }
    )
    return t_exam
