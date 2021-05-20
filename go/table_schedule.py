import time
import urllib
from lxml import html

etree = html.etree
import requests
import importlib, sys
from util import identifyRandcode
from db.model import t_es_schedule, t_unsuccessful_list
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
                        classes = current_student.getClass()
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
                    classes = current_student.getClass()
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
    t_es_schedule = dict(
        {
            'schedule': classes
        }
    )
    return t_es_schedule
