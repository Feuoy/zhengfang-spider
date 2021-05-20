import re
import time
import urllib
from table import for_grade_table
from bs4 import BeautifulSoup
from lxml import html
import json
import requests
import importlib, sys
from util import identifyRandcode
from db.model import t_unsuccessful_list, t_es_student, t_es_certification_exam, t_es_exam, t_tm_leave, t_tm_attendance
from db.model import t_es_schedule, t_es_grade, t_es_credit
import pandas as pd
etree = html.etree


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

    def getClass(self):
        try:
            urlStudentname = urllib.parse.quote_plus(str(self.studentName.encode('gb2312')))
        except UnicodeEncodeError:
            urlStudentname = urllib.parse.quote_plus(str(self.studentName.encode('utf-16')))
        kburl = "http://es.bnuz.edu.cn/jwgl/xskbcx.aspx?xh={0}&xm={1}&gnmkdm=N121601".format(str(self.studentNumber),
                                                                                             str(urlStudentname))
        refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        headers = {
            "Referer": refer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }
        response = self.s.get(kburl, headers=headers)
        html = response.content
        self.loginHtml = html
        soup = BeautifulSoup(html, "lxml")
        __VIEWSTATE = soup.findAll(name="input")[2]["value"]
        oneClassKeys = ['schoolYear', 'schoolTerm',
                        'studentNumber', 'electiveCourseNumber',
                        'serialDayOfWeek', 'serialLessonOfDay',
                        'lessonLength', 'singleOrDoubleWeek',
                        'startingWeek', 'endingWeek',
                        'curriculumSchedule',
                        'courseSelectionParameters',
                        'isSelected', 'courseTitle', 'courseTime',
                        'courseTeacher', 'courseClassroomLocation']
        oneClassValues = []
        classXqj = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        classes = []
        xkkhZip = self.getXKKHfromTest()
        if xkkhZip == "noExamThisTerm":
            return ""
        termList = soup.find_all("select")[0]
        term = termList.option['value']
        XN = term[0:len(term) - 1]
        term = term[len(term) - 1]
        trs = soup.find(id="table1").find_all('tr')
        tag = 0
        for tr in range(1, len(trs)):
            if (tr != 8 and tr != 11):
                tds = trs[tr].find_all('td')
                if (tr == 1 or tr == 5 or tr == 10):
                    xqj = -2
                else:
                    xqj = -1
                if (tag != 0):
                    xqj = xqj + tag
                tag = 0
                for td in tds:
                    xqj = xqj + 1
                    if td.string == None:
                        if (td.get('rowspan') != None):
                            if td["rowspan"] == '3':
                                tag = tag + 1
                        for child in td.children:
                            soup = BeautifulSoup(str(child), "lxml")
                            liList = soup.find_all('li')
                            for liTag in liList:
                                soup = BeautifulSoup(str(liTag), "lxml")
                                if (soup.li != None):
                                    if (soup.li['title'] == '上课时间地点'):
                                        liContent = soup.li
                                        soup.span.decompose()
                                        classContentList = liContent.contents
                                        if (soup.li.em != None):
                                            tag_em = soup.li.em
                                            classContentList = tag_em.contents
                                            if (str(classContentList[0]) == '<br/>'):
                                                continue
                                        classContent = ""
                                        for singleContent in classContentList:
                                            classContent = classContent + str(
                                                singleContent)
                                        contents = classContent.split('<br/>')
                                        isOne = 0
                                        if (len(contents) == 4):
                                            isOne = 1
                                            classContentReverse = classContent[::-1]
                                            skcd2 = classContentReverse.find('节')
                                            skcd1 = len(classContent) - skcd2 - 1
                                            skcd = classContent[skcd1 - 1]
                                            dsz1 = classContent.find('单周')
                                            dsz2 = classContent.find('双周')
                                            dsz = ""
                                            if (dsz1 != -1):
                                                dsz = "单"
                                            elif (dsz2 != -1):
                                                dsz = "双"
                                            qsz1 = classContent.find('{')
                                            qsz = classContent[qsz1 + 2]
                                            jsz3 = classContent.find('}')
                                            jsz2 = classContent.find('}')
                                            jsz2 = jsz2 - 1
                                            info = classContent[qsz1:jsz3 + 1]
                                            qsz2 = info.find('{')
                                            jsz4 = info.find(',')
                                            jsz5 = info.find('}')
                                            jsz5 = jsz5 - 1
                                            jsz7 = info.find('周')
                                            if (jsz4 != -1):
                                                jsz = []
                                                qsz = []
                                                dsz = []
                                                x = info[qsz2 + 2:jsz7]
                                                weeks = x.split(",")
                                                for week in weeks:
                                                    y = week.find('-')
                                                    if (y != -1):
                                                        qsz.append(week[0:y])
                                                        if (week[len(week) - 1] == "单" or week[len(week) - 1] == "双"):
                                                            jsz.append(week[y + 1:len(week) - 1])
                                                            if (week[len(week) - 1] == "单"):
                                                                dsz.append("单")
                                                            else:
                                                                dsz.append("双")
                                                        else:
                                                            jsz.append(week[y + 1:len(week)])
                                                            dsz.append("")
                                                    else:
                                                        qsz.append(week)
                                                        jsz.append(week)
                                                        dsz.append("")
                                            else:
                                                jsz1 = info.find('-')
                                                if (info[jsz5 - 1] == "单" or info[jsz5 - 1] == "双"):
                                                    if (jsz1 != -1):
                                                        jsz = info[jsz1 + 1:jsz5 - 1]
                                                        qsz = info[qsz2 + 2:jsz1]
                                                else:
                                                    if (jsz1 != -1):
                                                        jsz = info[jsz1 + 1:jsz5]
                                                        qsz = info[qsz2 + 2:jsz1]
                                                    else:
                                                        jsz = info[qsz2 + 2:jsz7]
                                                        qsz = info[qsz2 + 2:jsz7]
                                            xqj1 = classXqj[xqj - 1]
                                            cut1 = classContent.find('<')
                                            classInfo = classContent[0:cut1] + '<br>' + xqj1 + "第"
                                            if (skcd == '3'):
                                                classInfo = classInfo + str(tr) + "," + str(tr + 1) + "," + str(
                                                    tr + 2) + "节"
                                            elif (skcd == '2'):
                                                classInfo = classInfo + str(tr) + "," + str(tr + 1) + "节"
                                            elif (skcd == '1'):
                                                classInfo = classInfo + str(tr) + "节"
                                            cut2 = classContent.find('{')
                                            cut3 = classContent.find('}')
                                            classInfo = classInfo + classContent[cut2:cut3 + 1]
                                            cut4 = classContent.find('>')
                                            classInfo = classInfo + '<br>' + classContent[cut4 + 1:cut2] + '<br>'
                                            location = classContent.split('<br/>')[2]
                                            cut5 = location.find("(")
                                            classInfo = classInfo + location[0:cut5]
                                            classInfoList = classInfo.split('<br>')
                                            className = classInfoList[0]
                                            classTime = classInfoList[1]
                                            classTeacher = classInfoList[2]
                                            classLocation = classInfoList[3]
                                            if (jsz4 != -1):
                                                for i in range(0, len(jsz)):
                                                    oneClassValues = []
                                                    oneClassValues.append(XN)
                                                    oneClassValues.append(term)
                                                    oneClassValues.append(self.studentNumber)
                                                    oneClassValues.append(xkkhZip[classContentList[0]])
                                                    oneClassValues.append(xqj)
                                                    oneClassValues.append(tr)
                                                    oneClassValues.append(skcd)
                                                    oneClassValues.append(dsz[i])
                                                    oneClassValues.append(qsz[i])
                                                    oneClassValues.append(jsz[i])
                                                    oneClassValues.append(classInfo)
                                                    oneClassValues.append('')
                                                    oneClassValues.append('')
                                                    oneClassValues.append(className)
                                                    oneClassValues.append(classTime)
                                                    oneClassValues.append(classTeacher)
                                                    oneClassValues.append(classLocation)
                                                    oneClass = dict(
                                                        (key, value) for key, value in
                                                        zip(oneClassKeys, oneClassValues))
                                                    classes.append(oneClass)
                                            else:
                                                oneClassValues = []
                                                oneClassValues.append(XN)
                                                oneClassValues.append(term)
                                                oneClassValues.append(self.studentNumber)
                                                try:
                                                    oneClassValues.append(xkkhZip[classContentList[0]])
                                                except KeyError:
                                                    pass
                                                oneClassValues.append(xqj)
                                                oneClassValues.append(tr)
                                                oneClassValues.append(skcd)
                                                oneClassValues.append(dsz)
                                                oneClassValues.append(qsz)
                                                oneClassValues.append(jsz)
                                                oneClassValues.append(classInfo)
                                                oneClassValues.append('')
                                                oneClassValues.append('')
                                                oneClassValues.append(className)
                                                oneClassValues.append(classTime)
                                                oneClassValues.append(classTeacher)
                                                oneClassValues.append(classLocation)
                                                oneClass = dict(
                                                    (key, value) for key, value in zip(oneClassKeys, oneClassValues))
                                                classes.append(oneClass)
                                        else:
                                            isOne = 0
                                            length = len(contents) - 2
                                            num = 1
                                            for i in range(0, int(length / 2)):
                                                classContent = contents[0] + '<br/>' + contents[num] + '<br/>' + \
                                                               contents[num + 1] + '<br/>'
                                                num = num + 2
                                                classContentReverse = classContent[::-1]
                                                skcd2 = classContentReverse.find('节')
                                                skcd1 = len(classContent) - skcd2 - 1
                                                skcd = classContent[skcd1 - 1]
                                                dsz1 = classContent.find('单周')
                                                dsz2 = classContent.find('双周')
                                                dsz = ""
                                                if (dsz1 != -1):
                                                    dsz = "单"
                                                elif (dsz2 != -1):
                                                    dsz = "双"
                                                qsz1 = classContent.find('{')
                                                jsz3 = classContent.find('}')
                                                jsz2 = classContent.find('}')
                                                jsz2 = jsz2 - 1
                                                info = classContent[qsz1:jsz3 + 1]
                                                qsz2 = info.find('{')
                                                jsz4 = info.find(',')
                                                jsz5 = info.find('}')
                                                jsz5 = jsz5 - 1
                                                jsz7 = info.find('周')
                                                if (jsz4 != -1):
                                                    jsz = []
                                                    qsz = []
                                                    dsz = []
                                                    x = info[qsz2 + 2:jsz7]
                                                    weeks = x.split(",")
                                                    for week in weeks:
                                                        y = week.find('-')
                                                        if (y != -1):
                                                            qsz.append(week[0:y])
                                                            if (week[len(week) - 1] == "单" or week[
                                                                len(week) - 1] == "双"):
                                                                jsz.append(week[y + 1:len(week) - 1])
                                                                if (week[len(week) - 1] == "单"):
                                                                    dsz.append("单")
                                                                else:
                                                                    dsz.append("双")
                                                            else:
                                                                jsz.append(week[y + 1:len(week)])
                                                                dsz.append("")
                                                        else:
                                                            qsz.append(week)
                                                            jsz.append(week)
                                                            dsz.append("")
                                                else:
                                                    jsz1 = info.find('-')
                                                    if (info[jsz5 - 1] == "单" or info[jsz5 - 1] == "双"):
                                                        if (jsz1 != -1):
                                                            jsz = info[jsz1 + 1:jsz5 - 1]
                                                            qsz = info[qsz2 + 2:jsz1]
                                                    else:
                                                        if (jsz1 != -1):
                                                            jsz = info[jsz1 + 1:jsz5]
                                                            qsz = info[qsz2 + 2:jsz1]
                                                        else:
                                                            jsz = info[qsz2 + 2:jsz7]
                                                            qsz = info[qsz2 + 2:jsz7]
                                                xqj1 = classXqj[xqj - 1]
                                                cut1 = classContent.find('<')
                                                classInfo = classContent[0:cut1] + '<br>' + xqj1 + "第"
                                                if (skcd == '3'):
                                                    classInfo = classInfo + str(tr) + "," + str(tr + 1) + "," + str(
                                                        tr + 2) + "节"
                                                elif (skcd == '2'):
                                                    classInfo = classInfo + str(tr) + "," + str(tr + 1) + "节"
                                                elif (skcd == '1'):
                                                    classInfo = classInfo + str(tr) + "节"
                                                cut2 = classContent.find('{')
                                                cut3 = classContent.find('}')
                                                classInfo = classInfo + classContent[cut2:cut3 + 1]
                                                cut4 = classContent.find('>')
                                                classInfo = classInfo + '<br>' + classContent[cut4 + 1:cut2] + '<br>'
                                                location = classContent.split('<br/>')[2]
                                                cut5 = location.find("(")
                                                classInfo = classInfo + location[0:cut5]
                                                classInfoList = classInfo.split('<br>')
                                                className = classInfoList[0]
                                                classTime = classInfoList[1]
                                                classTeacher = classInfoList[2]
                                                classLocation = classInfoList[3]
                                                if (jsz4 != -1):
                                                    for i in range(0, len(jsz)):
                                                        oneClassValues = []
                                                        oneClassValues.append(XN)
                                                        oneClassValues.append(term)
                                                        oneClassValues.append(self.studentNumber)
                                                        oneClassValues.append(
                                                            xkkhZip[classContentList[0]])
                                                        oneClassValues.append(xqj)
                                                        oneClassValues.append(tr)
                                                        oneClassValues.append(skcd)
                                                        oneClassValues.append(dsz[i])
                                                        oneClassValues.append(qsz[i])
                                                        oneClassValues.append(jsz[i])
                                                        oneClassValues.append(classInfo)
                                                        oneClassValues.append('')
                                                        oneClassValues.append('')
                                                        oneClassValues.append(className)
                                                        oneClassValues.append(classTime)
                                                        oneClassValues.append(classTeacher)
                                                        oneClassValues.append(classLocation)
                                                        oneClass = dict(
                                                            (key, value) for key, value in
                                                            zip(oneClassKeys, oneClassValues))
                                                        classes.append(oneClass)
                                                else:
                                                    oneClassValues = []
                                                    oneClassValues.append(XN)
                                                    oneClassValues.append(term)
                                                    oneClassValues.append(self.studentNumber)
                                                    oneClassValues.append(xkkhZip[classContentList[0]])
                                                    oneClassValues.append(xqj)
                                                    oneClassValues.append(tr)
                                                    oneClassValues.append(skcd)
                                                    oneClassValues.append(dsz)
                                                    oneClassValues.append(qsz)
                                                    oneClassValues.append(jsz)
                                                    oneClassValues.append(classInfo)
                                                    oneClassValues.append('')
                                                    oneClassValues.append('')
                                                    oneClassValues.append(className)
                                                    oneClassValues.append(classTime)
                                                    oneClassValues.append(classTeacher)
                                                    oneClassValues.append(classLocation)
                                                    oneClass = dict(
                                                        (key, value) for key, value in
                                                        zip(oneClassKeys, oneClassValues))
                                                    classes.append(oneClass)
                                    else:
                                        break
        stunumber = classes[0]['studentNumber']
        while True:
            isExist = t_es_schedule.get_or_none(t_es_schedule.studentNumber == stunumber)
            if isExist:
                s = t_es_schedule.get(t_es_schedule.studentNumber == stunumber)
                s.delete_instance()
            else:
                break
        for each in classes:
            single = t_es_schedule(
                schoolYear=each['schoolYear'],
                schoolTerm=each['schoolTerm'],
                studentNumber=each['studentNumber'],
                electiveCourseNumber=each['electiveCourseNumber'],
                serialDayOfWeek=each['serialDayOfWeek'],
                serialLessonOfDay=each['serialLessonOfDay'],
                lessonLength=each['lessonLength'],
                singleOrDoubleWeek=each['singleOrDoubleWeek'],
                startingWeek=each['startingWeek'],
                endingWeek=each['endingWeek'],
                curriculumSchedule=each['curriculumSchedule'],
                courseSelectionParameters=each['courseSelectionParameters'],
                isSelected=each['isSelected'],
                courseTitle=each['courseTitle'],
                courseTime=each['courseTime'],
                courseTeacher=each['courseTeacher'],
                courseClassroomLocation=each['courseClassroomLocation']
            )
            single.save()
        return classes

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

    def getPersionInfo(self, studentNumber, password):
        info_url = "http://es.bnuz.edu.cn/jwgl/xsgrxx.aspx?xh=" + str(self.studentNumber) + "&xm=" + str(
            self.studentName) + "&gnmkdm=N121501"
        refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        headers = {
            "Referer": refer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }
        response = self.s.post(info_url, headers=headers)
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(content, "lxml")
        info = t_es_student(
            XH=soup.find(id="xh").string,
            XM=soup.find(id="xm").string,
            XSMM=password,
            XY=soup.find(id="lbl_xy").string,
            ZYMC=soup.find(id="lbl_zymc").string,
            CSRQ=soup.find(id="csrq").string,
            SFZH=soup.find(id="lbl_sfzh").string,
            ZZMM=soup.find(id="lbl_zzmm").string,
            MZ=soup.find(id="lbl_mz").string,
            XZB=soup.find(id="lbl_xzb").string,
            XZ=soup.find(id="lbl_xz").string,
            DQSZJ=soup.find(id="lbl_dqszj").string,
            XJZT=soup.find(id="lbl_xjzt").string,
            XSLB="",
            ZYDM="",
            CC=soup.find(id="lbl_CC").string,
            XB=soup.find(id="lbl_xb").string,
        )
        print(info)
        s = t_es_student.get_or_none(XH=soup.find(id="xh").string)
        1 if s else info.save(force_insert=True)

    def getCredit(self, studentNumber):
        xuefen_url = "http://es.bnuz.edu.cn/jwgl/xscjcx.aspx?xh=" + str(self.studentNumber) + "&xm=" + str(
            self.studentName) + "&gnmkdm=N121605"
        refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        headers = {
            "Referer": refer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }
        response = self.s.post(xuefen_url, headers=headers)
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(content, "lxml")
        trs = soup.find(id="gv_xf").findAll("tr")[1:]
        CreditStatistics_list = []
        for tr in trs:
            tds = tr.findAll("td")
            oneCreditKeys = [
                "curriculumNature",
                "creditRequirement",
                "creditObtained",
                "creditTaking",
                "creditPreselected",
                "creditLack"
            ]
            oneCreditValues = []
            for td in tds:
                if td.string == "\xa0":
                    td.string = ''
                oneCreditValues.append(td.string)
            oneCredit = {}
            oneCredit["studentNumber"] = studentNumber
            oneCredit_temp = dict((key, value) for key, value in zip(oneCreditKeys, oneCreditValues))
            oneCredit.update(oneCredit_temp)
            CreditStatistics_list.append(oneCredit)
        stunumber = CreditStatistics_list[0]['studentNumber']
        while True:
            isExist = t_es_credit.get_or_none(t_es_credit.studentNumber == stunumber)
            if isExist:
                s = t_es_credit.get(t_es_credit.studentNumber == stunumber)
                s.delete_instance()
            else:
                break
        for each in CreditStatistics_list:
            single = t_es_credit(
                studentNumber=each['studentNumber'],
                curriculumNature=each['curriculumNature'],
                creditRequirement=each['creditRequirement'],
                creditObtained=each['creditObtained'],
                creditTaking=each['creditTaking'],
                creditPreselected=each['creditPreselected'],
                creditLack=each['creditLack']
            )
            single.save(force_insert=True)
        return CreditStatistics_list

    def getCertification(self, studentNumber):
        dengji_url = "http://es.bnuz.edu.cn/xsdjkscx.aspx?xh=" + str(self.studentNumber) + "&xm=" + str(
            self.studentName) + "&gnmkdm=N121606"
        refer = "http://es.bnuz.edu.cn/jwgl/xs_main.aspx?xh=" + str(self.studentNumber)
        headers = {
            "Referer": refer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }
        response = self.s.post(dengji_url, headers=headers)
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(content, "lxml")
        trs = soup.find(id="DataGrid1").findAll("tr")[1:]
        Certification_list = []
        for tr in trs:
            tds = tr.findAll("td")
            oneCertificationKeys = [
                "XN",
                "XQ",
                "DJKSMC",
                "ZKZH",
                "KSRQ",
                "CJ",
                "TLCJ",
                "YDCJ",
                "XZCJ",
                "ZHCJ"
            ]
            oneCertificationValues = []
            for td in tds:
                if td.string == "\xa0":
                    td.string = ''
                oneCertificationValues.append(td.string)
            oneCertification = {}
            oneCertification_temp = dict(
                (key, value) for key, value in zip(oneCertificationKeys, oneCertificationValues))
            oneCertification.update(oneCertification_temp)
            Certification_list.append(oneCertification)
        while True:
            isExist = t_es_certification_exam.get_or_none(t_es_certification_exam.XH == str(self.studentNumber))
            if isExist:
                s = t_es_certification_exam.get(t_es_certification_exam.XH == str(self.studentNumber))
                s.delete_instance()
            else:
                break
        for each in Certification_list:
            single = t_es_certification_exam(
                XN=each['XN'],
                XQ=each['XQ'],
                XH=str(self.studentNumber),
                XM=str(self.studentName),
                DJKSMC=each['DJKSMC'],
                KSRQ=each['KSRQ'],
                CJ=each['CJ'],
                ZKZH=each['ZKZH'],
                TLCJ=each['TLCJ'],
                YDCJ=each['YDCJ'],
                XZCJ=each['XZCJ'],
                ZHCJ=each['ZHCJ'],
            )
            single.save(force_insert=True)
        return Certification_list

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


def go(studentNumber, studentPassword):
    start = time.clock()
    unsuccessful_list = pd.DataFrame(data=[])
    i = 0
    while i < 1:
        if 1:
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
                        classes = current_student.getClass()
                    except IndexError:
                        reason = 'outside school'
                        print(reason)
                        error_info = t_unsuccessful_list(serialNumber=i, studentNumber=studentNumber,
                                                         studentPassword=studentPassword, reason=reason)
                        error_info.save()
                    else:
                        grade = current_student.getScore()
                        credit = current_student.getCredit(studentNumber)
                        current_student.getPersionInfo(studentNumber, studentPassword)
                        certification = current_student.getCertification(studentNumber)
                        exam = current_student.getExam(studentNumber)
                        tm = getTm(studentNumber, studentPassword)
                        current_student.login_out()
                        print("successfully！")
            else:
                print("login successfully！")
                try:
                    classes = current_student.getClass()
                except IndexError:
                    reason = 'outside school'
                    print(reason)
                    error_info = t_unsuccessful_list(serialNumber=i, studentNumber=studentNumber,
                                                     studentPassword=studentPassword, reason=reason)
                    error_info.save()
                else:
                    grade = current_student.getScore()
                    credit = current_student.getCredit(studentNumber)
                    current_student.getPersionInfo(studentNumber, studentPassword)
                    certification = current_student.getCertification(studentNumber)
                    exam = current_student.getExam(studentNumber)
                    tm = getTm(studentNumber, studentPassword)
                    current_student.login_out()
                    print("successfully！")
        else:
            pass
        i = i + 1
    end = time.clock()
    print(end - start)
    result = dict(
        {
            'schedule': classes,
            'grade': grade,
            'credit': credit,
            'certification': certification,
            'exam': exam,
            'tm': tm
        }
    )
    return result
