from bs4 import BeautifulSoup


def get_gradepast(Grade_temp):
    list_1 = []
    for i in range(len(Grade_temp)):
        dict_1 = {}
        dict_1['schoolYear'] = Grade_temp[i]['schoolYear']
        dict_1['schoolTerm'] = Grade_temp[i]['schoolTerm']
        list_1.append(dict_1)
    list_2 = []
    for i in range(len(list_1)):
        list_2.append(str(list_1[i]))
    list_3 = set(list_2)
    list_4 = list(list_3)
    grade_past = []
    for i in range(len(list_4)):
        dict_5 = {}
        dict_5["schoolYear"] = list_4[i][16:25]
        dict_5["schoolTerm"] = list_4[i][-3]
        grade_past.append(dict_5)
    return grade_past


def getGrade(chengji_html_str):
    soup = BeautifulSoup(chengji_html_str, "lxml")
    trs = soup.find(id="gv_xscj").findAll("tr")[1:]
    Grade = []
    for tr in trs:
        tds = tr.findAll("td")
        tds[3:4] = tr.findAll("a")
        tds = tds + tds[6:7]
        new_tds = tds[0:1] + tds[1:2] \
                  + tds[14:15] + tds[14:15] + tds[14:15] \
                  + tds[3:4] + tds[2:3] \
                  + tds[7:8] + tds[9:10] \
                  + tds[14:15] \
                  + tds[8:9] \
                  + tds[14:15] \
                  + tds[14:15] + tds[14:15] \
                  + tds[11:12] \
                  + tds[14:15] + tds[14:15] \
                  + tds[5:6]
        oneGradeKeys = ["schoolYear", "schoolTerm",
                        "electiveCourseNumber", "studentNumber", "studentName",
                        "courseTitle", "courseCode",
                        "credit", "score",
                        "scoreConverted",
                        "gradePointAverage",
                        "CXBJ",
                        "peacetimeScore", "experimentalScore",
                        "makeUpExaminationScore",
                        "CXCJ", "TJ",
                        "curriculumNature",
                        ]
        oneGradeValues = []
        for td in new_tds:
            oneGradeValues.append(td.string)
        oneGrade = dict((key, value) for key, value in zip(oneGradeKeys, oneGradeValues))
        Grade.append(oneGrade)
    return Grade


def getCourseNumber(html):
    soup = BeautifulSoup(html, "lxml")
    Course = []
    try:
        trs = soup.find(id="gv_xk").findAll("tr")[1:]
    except AttributeError:
        pass
    else:
        for tr in trs:
            tds = tr.findAll("td")
            new_tds = tds[0:2]
            oneCourseKeys = ["electiveCourseNumber", "courseTitle"]
            oneCourseValues = []
            for td in new_tds:
                oneCourseValues.append(td.string)
            oneCourse = dict((key, value) for key, value in zip(oneCourseKeys, oneCourseValues))
            Course.append(oneCourse)
        try:
            trs_2 = soup.find(id="DataGrid2").findAll("tr")[1:]
        except AttributeError:
            pass
        else:
            for tr_2 in trs_2:
                tds_2 = tr_2.findAll("td")
                new_tds_2 = tds_2[0:2]
                oneCourseKeys_2 = ["electiveCourseNumber", "courseTitle"]
                oneCourseValues_2 = []
                for td_2 in new_tds_2:
                    oneCourseValues_2.append(td_2.string)
                oneCourse_2 = dict((key, value) for key, value in zip(oneCourseKeys_2, oneCourseValues_2))
                Course.append(oneCourse_2)
    return Course


def get_t_grade(Grade, all_Course, student_number, student_name):
    grade = Grade
    course = all_Course
    for i in range(len(grade)):
        for j in range(len(course)):
            if grade[i]['courseTitle'] == course[j]['courseTitle'] \
                    and str(grade[i]['schoolYear'] + "-" + grade[i]['schoolTerm']) == str(
                course[j]['electiveCourseNumber'][1:12]) \
                    and grade[i]['courseCode'] == course[j]['electiveCourseNumber'][14:22]:
                grade[i]['electiveCourseNumber'] = course[j]['electiveCourseNumber']
    for i in range(len(grade)):
        if grade[i]['electiveCourseNumber'] == '\xa0' \
                or grade[i]['electiveCourseNumber'] == '\xa0' == '':
            grade[i]['electiveCourseNumber'] = str(
                "(" + grade[i]['schoolYear'] + "-" + grade[i]['schoolTerm'] + ")-" + grade[i]['courseCode'])
    for i in range(len(grade)):
        if grade[i]['electiveCourseNumber'] == '是':
            grade[i]['electiveCourseNumber'] = str(
                "(" + grade[i]['schoolYear'] + "-" + grade[i]['schoolTerm'] + ")-" + grade[i]['courseCode'])
    for i in range(len(grade)):
        if grade[i]['makeUpExaminationScore'] == "\xa0":
            grade[i]['makeUpExaminationScore'] = ""
    for i in range(len(grade)):
        grade[i]['studentNumber'] = student_number
        grade[i]['studentName'] = student_name
        grade[i]['scoreConverted'] = ""
        grade[i]['CXBJ'] = "0"
        grade[i]['peacetimeScore'] = ""
        grade[i]['experimentalScore'] = ""
        grade[i]['CXCJ'] = ""
        grade[i]['TJ'] = ""
    return grade


def get_grade_table(student_number, student_name, chengji_html_str, jiaoping_html_str_list):
    all_Course = []
    Grade = getGrade(chengji_html_str)
    grade_past = get_gradepast(Grade)
    for i in range(len(grade_past)):
        Course = getCourseNumber(jiaoping_html_str_list[i])
        all_Course = all_Course + Course
    grade = get_t_grade(Grade, all_Course, student_number, student_name)
    return grade
