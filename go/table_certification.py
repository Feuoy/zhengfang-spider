import time
from lxml import html
import requests
import importlib, sys
from util import identifyRandcode
from db.model import t_unsuccessful_list, t_es_certification_exam
from bs4 import BeautifulSoup
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
        nnn = 1
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
                        Certification_list = current_student.getCertification(studentNumber)
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
                    Certification_list = current_student.getCertification(studentNumber)
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
    t_es_certification = dict(
        {
            'certification': Certification_list
        }
    )
    return t_es_certification
