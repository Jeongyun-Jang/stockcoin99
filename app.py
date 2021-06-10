from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = 'SPARTA'
#client = MongoClient('52.78.209.2', 27017, username="test", password="test")
client = MongoClient('localhost', 27017)
db = client.dbsparta_week1

# 메인페이지
@app.route('/')
def main():
    token_receive = request.cookies.get('mytoken')
    if token_receive is None:
        return render_template("main.html")
    else:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({'username': payload['id']})
            return render_template('main.html', user_info=user_info)
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login', msg='로그인 시간이 만료되었습니다.'))
        except jwt.exceptions.DecodeError:
            return redirect(url_for('login', msg='로그인 정보가 존재하지 않습니다.'))

# 회원가입 로그인
@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({'username': username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "password": password_hash
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success' })

@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': password_hash})
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 인덱스 페이지 카드들 정보 보내기기
@app.route('/getcard', methods=['GET'])
def get_card():
    type_receive = request.args.get('type_give')
    token_receive = request.cookies.get('mytoken')
    if token_receive:
        try:
            if type_receive == "coin":
                result = list(db.applist.find({'type': '코인거래소'}, {'_id': False}))
            else:
                result = list(db.applist.find({'type': '증권'}, {'_id': False}))
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({'username': payload['id']})
            return render_template('index.html', user_info=user_info, result=result )
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("main"))
    else:
        if type_receive == "coin":
            result = list(db.applist.find({'type':'코인거래소'},{'_id':False}))
            return render_template("index.html", result=result)
        else:
            result = list(db.applist.find({'type': '증권'}, {'_id': False}))
            return render_template("index.html", result=result)

# index.html에서 선택한 카드 세부 정보 detail.html에 보내기
@app.route('/get_detail_Test', methods=['GET'])
def get_detail_card():
    type_receive = request.args.get('type_give')
    result = db.applist.find_one({'app_name':type_receive})
    result2 = list(db.review.find({'app_name':type_receive},{'_id':False}))
    return render_template("detail.html", result=result, result2=result2)

#detail.html에서 작성한 리뷰 review DB에 저장
@app.route('/review', methods=['POST'])
def write_review():
    appname_receive = request.form['appname_give']
    comment_receive = request.form['comment_give']
    star1 = int(request.form['star1_give'])
    star2 = int(request.form['star2_give'])
    star3 = int(request.form['star3_give'])
    star4 = int(request.form['star4_give'])

    star_avg = round( (star1+star2+star3+star4)/4 , 1) #user에게 입력 받은 star들 평균 star_avg에 저장

    #find = db.applist.find_one({'appname': appname_receive})
    #print(find)

    print(star_avg)

    doc={
        'appname': appname_receive,
        'comment': comment_receive,
        'star1': star1,
        'star2': star2,
        'star3': star3,
        'star4': star4
    }
    db.review.insert_one(doc)




    return jsonify({'msg':'저장 완료!'})

'''
#리뷰정보 불러오기
@app.route('/review_get_card', methods=['POST'])
def review_get_card():
    stars_avg_list = [0,0,0,0]
    title_receive = request.form['title_give']
    print(title_receive)
    reviews = list(db.review.find({'app_name':title_receive},{'_id':False})) #app_name,comment,star1,star2,star3,star4 (+add userID)
    print(reviews)
    review_cnt = len(reviews)
    print(review_cnt)

    for review in reviews:
        stars_avg_list[0] += int(review['star1'])
        stars_avg_list[1] += int(review['star2'])
        stars_avg_list[2] += int(review['star3'])
        stars_avg_list[3] += int(review['star4'])

    stars_avg_list[0] /=review_cnt
    stars_avg_list[1] /=review_cnt
    stars_avg_list[2] /=review_cnt
    stars_avg_list[3] /=review_cnt

    print(stars_avg_list)


    return jsonify({"result": "success", "reviews": reviews, "review_cnt": review_cnt,'stars_avg_list':stars_avg_list})

'''



'''
#detail 정보 불러오기
@app.route('/detail_get_card', methods=['POST'])
def detail_get_card():
    title_receive = request.form['title_give']
    print(title_receive)
    reviews = list(db.applist.find({'app_name':title_receive},{'_id':False})) #type,company,app_name,image_url,google_url
    print(reviews)
    return jsonify({"result": "success", "reviews": reviews})
'''

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)