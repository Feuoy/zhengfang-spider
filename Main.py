from flask import Flask
from flask import request
from flask import jsonify
from go import table_grade, table_certification, table_exam, table_tm, table_schedule, table_credit, login
from util import identifyRandcode


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/tk', methods=['post', 'get'])
def tk():
    p = request.args.get('p')
    type = request.args.get('type')
    print(p)
    print(type)
    return jsonify({'t': [p, type]})


@app.route('/data', methods=['post'])
def data():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    result = login.go(studentnumber, password)
    return jsonify(result)


@app.route('/schedule', methods=['post'])
def schedule():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    t_es_schedule = table_schedule.go(studentnumber, password)
    return jsonify(t_es_schedule)


@app.route('/grade', methods=['post'])
def grade():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    t_es_grade = table_grade.go(studentnumber, password)
    return jsonify(t_es_grade)


@app.route('/credit', methods=['post'])
def credit():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    t_es_credit = table_credit.go(studentnumber, password)
    return jsonify(t_es_credit)


@app.route('/certification', methods=['post'])
def certification():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    t_es_certification = table_certification.go(studentnumber, password)
    return jsonify(t_es_certification)


@app.route('/exam', methods=['post'])
def exam():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    t_es_exam = table_exam.go(studentnumber, password)
    return jsonify(t_es_exam)


@app.route('/tm', methods=['post'])
def tm():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    t_tm = table_tm.go(studentnumber, password)
    return jsonify(t_tm)


@app.route('/login', methods=['post'])
def loginIn():
    data = request.json
    studentnumber = data['studentnumber']
    password = data['password']
    current_student = login.student(studentnumber, password)
    current_student.getCheckCodeImage()
    orginalCheckCode = identifyRandcode.identify_randcode('image/original_img.jpg',
                                                          'image/adjusted_img.jpg')
    checkCode = orginalCheckCode[0:5]
    current_student.login(checkCode)
    return jsonify({"code": "200", "data": "success"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
