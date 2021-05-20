from peewee import *

db = MySQLDatabase(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="bnuz_app_db"
)

db.connect()


class t_es_schedule(Model):
    schoolYear = CharField(null=False)
    schoolTerm = CharField(null=False)
    studentNumber = CharField(null=False)
    electiveCourseNumber = CharField(null=False)
    serialDayOfWeek = CharField(null=False)
    serialLessonOfDay = CharField(null=False)
    lessonLength = CharField(null=False)
    singleOrDoubleWeek = CharField(null=True)
    startingWeek = CharField(null=False)
    endingWeek = CharField(null=False)
    curriculumSchedule = CharField(null=True)
    courseSelectionParameters = CharField(null=True)
    isSelected = CharField(null=True)
    courseTitle = CharField(null=False)
    courseTime = CharField(null=False)
    courseTeacher = CharField(null=False)
    courseClassroomLocation = CharField(null=False)

    class Meta:
        database = db


class t_es_grade(Model):
    schoolYear = CharField(null=True)
    schoolTerm = CharField(null=True)
    electiveCourseNumber = CharField(null=False)
    studentNumber = CharField(null=False)
    studentName = CharField(null=True)
    courseTitle = CharField(null=True)
    courseCode = CharField(null=True)
    credit = CharField(null=True)
    score = CharField(null=True)
    scoreConverted = CharField(null=True)
    gradePointAverage = CharField(null=True)
    CXBJ = CharField(null=True)
    peacetimeScore = CharField(null=True)
    experimentalScore = CharField(null=True)
    makeUpExaminationScore = CharField(null=True)
    CXCJ = CharField(null=True)
    TJ = CharField(null=True)
    curriculumNature = CharField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('electiveCourseNumber', 'studentNumber')


class t_es_credit(Model):
    studentNumber = CharField(null=False)
    curriculumNature = CharField(null=True)
    creditRequirement = CharField(null=True)
    creditObtained = CharField(null=True)
    creditTaking = CharField(null=True)
    creditPreselected = CharField(null=True)
    creditLack = CharField(null=True)

    class Meta:
        database = db


class t_es_student(Model):
    XH = CharField(null=False, primary_key=True)
    XM = CharField(null=False)
    XSMM = CharField()
    XY = CharField(null=False)
    ZYMC = CharField(null=False)
    CSRQ = CharField(null=False)
    SFZH = CharField(null=False)
    ZZMM = CharField(null=False)
    MZ = CharField(null=False)
    XZB = CharField(null=False)
    XZ = CharField(null=False)
    DQSZJ = CharField(null=False)
    XJZT = CharField()
    XSLB = CharField()
    ZYDM = CharField()
    CC = CharField()
    XB = CharField(null=False)

    class Meta:
        database = db


class t_es_certification_exam(Model):
    XN = CharField(null=False)
    XQ = IntegerField(null=False)
    XH = CharField(null=False)
    XM = CharField(null=True)
    DJKSMC = CharField(null=False)
    KSRQ = CharField(null=True)
    CJ = CharField(null=True)
    BZ = CharField(null=True)
    SFSQMX = CharField(null=True)
    SFZH = CharField(null=True)
    ZKZH = CharField(null=True)
    TLCJ = CharField(null=True)
    YDCJ = CharField(null=True)
    XZCJ = CharField(null=True)
    ZHCJ = CharField(null=True)
    PTHDJ = CharField(null=True)
    KYCJ = CharField(null=True)
    KYZKZ = CharField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('XN', 'XQ', 'XH', 'DJKSMC')


class t_es_exam(Model):
    studentNumber = CharField(null=False)
    examIndex = CharField(null=False)
    classSetDepartment = CharField(null=False)
    electiveCourseNumber = CharField(null=False)
    courseName = CharField(null=False)
    startWeek = CharField(null=False)
    endWeek = CharField(null=False)
    examTimeOrCourseTime = CharField(null=False)
    classroom = CharField(null=False)
    seatNumber = CharField(null=False)
    remark = CharField(null=True)
    slowExamination = CharField(null=True)

    class Meta:
        database = db


class t_tm_leave(Model):
    studentNumber = CharField(null=False)
    leave_id = CharField(null=False)
    type = CharField(null=False)
    reason = CharField(null=False)
    status = CharField(null=False)
    dateCreated = CharField(null=False)

    class Meta:
        database = db
        primary_key = CompositeKey('studentNumber', 'leave_id')


class t_tm_attendance(Model):
    studentNumber = CharField(null=False)
    attendance_id = CharField(null=False)
    course = CharField(null=False)
    courseItem = CharField(null=False)
    teacher = CharField(null=False)
    week = CharField(null=False)
    dayOfWeek = CharField(null=False)
    startSection = CharField(null=False)
    totalSection = CharField(null=False)
    type = CharField(null=False)
    version = CharField(null=True)
    freeListenFormId = CharField(null=True)
    studentLeaveFormId = CharField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('studentNumber', 'attendance_id')


class t_unsuccessful_list(Model):
    serialNumber = CharField(null=False)
    studentNumber = CharField(null=False)
    studentPassword = CharField(null=False)
    reason = CharField(null=False)

    class Meta:
        database = db


t_es_schedule.create_table()
t_es_grade.create_table()
t_es_credit.create_table()
t_es_student.create_table()
t_es_certification_exam.create_table()
t_es_exam.create_table()

t_tm_leave.create_table()
t_tm_attendance.create_table()

t_unsuccessful_list.create_table()
