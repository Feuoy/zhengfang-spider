import re
import time
import urllib
from table import for_grade_table
from bs4 import BeautifulSoup
from lxml import html
etree = html.etree
import requests
import importlib, sys
from util import identifyRandcode
from db.model import t_es_grade, t_unsuccessful_list
import pandas as pd
import os


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

    def getXKKHfromTest(self):
        url = "http://es.bnuz.edu.cn/jwgl/xskscx.aspx?xh=" + str(self.studentNumber) + "&xm=" \
              + str(self.studentName) + "&gnmkdm=N121604"
        refer_url = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        header = {
            'Referer': refer_url,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip,deflate'
        }
        response = self.s.get(url, headers=header)
        selector = etree.HTML(response.content)
        __VIEWSTATE = selector.xpath('//*[@id="__VIEWSTATE"][1]/@value')[0]
        ccd_xn_ClientState = selector.xpath('//*[@id="ccd_xn_ClientState"]/@value')[0]
        ccd_xq_ClientState = selector.xpath('//*[@id="ccd_xq_ClientState"]/@value')[0]
        csurl = "http://es.bnuz.edu.cn/jwgl/xskscx.aspx?xh=" + str(self.studentNumber) + "&xm=" + str(
            self.studentName) + "&gnmkdm=N121604"
        refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        origin = "http: // es.bnuz.edu.cn"
        headers = {
            "Referer": refer,
            "Host": "es.bnuz.edu.cn",
            "Origin": origin,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }
        formdata = {
            "__VIEWSTATE": __VIEWSTATE,
            "ccd_xn_ClientState": ccd_xn_ClientState,
            "ccd_xq_ClientState": ccd_xq_ClientState,
            "ScriptManager1": "ScriptManager1|bt_kscx",
            "__VIEWSTATEENCRYPTED": "",
            "__ASYNCPOST": "true",
            "bt_kscx": "考试查询"
        }
        className = []
        classCode = []
        response = self.s.post(csurl, headers=headers, data=formdata)
        html = response.content.decode("utf-8")
        soup = BeautifulSoup(html, "lxml")
        try:
            table = soup.find_all("table")[0]
        except IndexError:
            return "noExamThisTerm"
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            if (tds != []):
                code = tds[2].string
                name = tds[3].string
                className.append(name)
                classCode.append(code)
        classInfo = dict((key, value) for key, value in zip(className, classCode))
        return classInfo

    def getScore(self):
        url = "http://es.bnuz.edu.cn/jwgl/xscjcx.aspx?xh=" + str(self.studentNumber) + "&xm=" \
              + str(self.studentName) + "&gnmkdm=N121605"
        refer_url = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        header = {
            'Referer': refer_url,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip,deflate'
        }
        response = self.s.get(url, headers=header)
        soup = BeautifulSoup(response.content, "lxml")
        pre = soup.find(id="__VIEWSTATE")
        __VIEWSTATE = (re.findall(r'value="(.*)"', str(pre)))[0]
        cjurl = "http://es.bnuz.edu.cn/jwgl/xscjcx.aspx?xh=" + str(self.studentNumber) + "&xm=" + str(
            self.studentName) + "&gnmkdm=N121605"
        refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        headers = {
            "Referer": refer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }
        formdata = {
            "__VIEWSTATE": __VIEWSTATE,
            "ScriptManager1": "ScriptManager1|Button2",
            "__VIEWSTATEENCRYPTED": "",
            "__ASYNCPOST": "true",
            "Button2": "在校学习成绩查询"
        }
        response = self.s.post(cjurl, headers=headers, data=formdata)
        chengji_html_str = response.content
        Grade = for_grade_table.getGrade(chengji_html_str)
        grade_past = for_grade_table.get_gradepast(Grade)
        try:
            urlStudentname = urllib.parse.quote_plus(str(self.studentName.encode('gb2312')))
        except UnicodeEncodeError:
            urlStudentname = urllib.parse.quote_plus(str(self.studentName.encode('utf-16')))
        url_courseNumber = "http://es.bnuz.edu.cn/jwgl/xsxkqk.aspx?xh=" + str(self.studentNumber) + "&xm=" \
                           + str(urlStudentname) + "&gnmkdm=N121615"
        refer_url_courseNumber = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        header_courseNumber = {
            'Referer': refer_url_courseNumber,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip,deflate'
        }
        response_courseNumber = self.s.get(url_courseNumber, headers=header_courseNumber)
        soup_courseNumber = BeautifulSoup(response_courseNumber.content, "lxml")
        pre_courseNumber = soup_courseNumber.find(id="__VIEWSTATE")
        __VIEWSTATE_courseNumber = str(pre_courseNumber).split("value=")[1][1:-3]
        jiaoping_html_str_list = []
        for i in range(len(grade_past)):
            for_courseNumber_formdata = {
                '__VIEWSTATE': __VIEWSTATE_courseNumber,
                'ddlXN': grade_past[i]["schoolYear"],
                'ddlXQ': grade_past[i]["schoolTerm"],
                'btn': ' 查 询 '
            }
            for_courseNumber_url = "http://es.bnuz.edu.cn/xsxkqk.aspx?xh=" + str(self.studentNumber) + "&xm=" + str(
                urlStudentname) + "&gnmkdm=N121615"
            refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
            for_courseNumber_headers = {
                "Referer": refer,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
            }
            r = self.s.post(for_courseNumber_url, headers=for_courseNumber_headers, data=for_courseNumber_formdata)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            for_courseNumber_current_html = str(r.content.decode("utf-8").encode('utf-16').decode("utf-16"))
            jiaoping_html_str_list.append(for_courseNumber_current_html)
        grade = for_grade_table.get_grade_table(self.studentNumber, self.studentName, response.content,
                                                jiaoping_html_str_list)
        stunumber = grade[0]['studentNumber']
        while True:
            isExist = t_es_grade.get_or_none(t_es_grade.studentNumber == stunumber)
            if isExist:
                s = t_es_grade.get(t_es_grade.studentNumber == stunumber)
                s.delete_instance()
            else:
                break
        for each in grade:
            single = t_es_grade(
                schoolYear=each['schoolYear'],
                schoolTerm=each['schoolTerm'],
                electiveCourseNumber=each['electiveCourseNumber'],
                studentNumber=each['studentNumber'],
                studentName=each['studentName'],
                courseTitle=each['courseTitle'],
                courseCode=each['courseCode'],
                credit=each['credit'],
                score=each['score'],
                scoreConverted=each['scoreConverted'],
                gradePointAverage=each['gradePointAverage'],
                CXBJ=each['CXBJ'],
                peacetimeScore=each['peacetimeScore'],
                experimentalScore=each['experimentalScore'],
                makeUpExaminationScore=each['makeUpExaminationScore'],
                CXCJ=each['CXCJ'],
                TJ=each['TJ'],
                curriculumNature=each['curriculumNature']
            )
            single.save(force_insert=True)
        return grade


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
                        grade = current_student.getScore()
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
                    grade = current_student.getScore()
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
    t_es_grade = dict(
        {
            'grade': grade
        }
    )
    return t_es_grade
