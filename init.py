from functools import wraps
from flask import Flask, request, render_template, redirect, jsonify, session, url_for, g
from flask_socketio import SocketIO, rooms, close_room, join_room, leave_room
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
from random import randint
import numpy
import time
from package import dictionary
import json
from pywebpush import webpush
from markupsafe import Markup, escape

import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'jhemin0415@gmail.com',
    MAIL_PASSWORD = 'djdkdl8255',

    MYSQL_DATABASE_USER = 'jhemin0415',
    MYSQL_DATABASE_PASSWORD = '7dj1dk4dl4!@',
    MYSQL_DATABASE_DB = 'treechat',
    UPLOAD_FOLDER = '/static/upload'
)
app.secret_key = 'treechat'
mysql = MySQL()
mysql.init_app(app)
mail = Mail(app)
socketio = SocketIO(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id', None) is None:
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated_function

def generate_number():
    conn = mysql.connect()
    cur = conn.cursor()
    try:
        cur.execute('select number from number_log')
        result = cur.fetchall()
    finally:
        conn.close()

    while 1:
        number = randint(1,999999999)
        if result:
            if number not in result[0]:
                return number
        else:
            return number

@app.route('/', methods=['GET','POST'])
def main():
    if request.method == 'POST':
        conn = mysql.connect()
        cur = conn.cursor()
        data = request.get_json()
        success = {'success':'0'}
        try:
            cur.execute('select * from account where id = %s;', (data['id'], ))
            result = cur.fetchone()
        finally:
            conn.close()
        if result:
            if check_password_hash(result[1].decode(), data['password']):
                session['id'] = result[0]; session['email'] = result[2]
                session['nickname'] = result[3]; session['message'] = result[4]
                success['success'] = '1'

        return jsonify(success)

    return render_template('main.html', time=time.time())

@app.route('/register', methods=["POST"])
def menu():
    if request.method == 'POST':

        data = request.get_json()
        conn = mysql.connect()
        cur = conn.cursor()
        try:
            cur.execute('select id from account where id = %s', (data['id']))
            id_result_data = cur.fetchone()
            cur.execute('select email from account where email = %s', (data['email']))
            email_result_data = cur.fetchone()
        finally:
            conn.close()

        if id_result_data:
            return jsonify(event = 'id_overlap')
        if email_result_data:
            return jsonify(event = 'email_overlap')

        try:
            conn.connect()
            cur.execute('insert into account (id, passwd, email, nickname) values (%s, %s, %s, %s)',
                        (data['id'], generate_password_hash(data['password']), data['email'], data['id']))
            conn.commit()
        finally:
            conn.close()
        return jsonify(event = 'success')

@app.route('/profile')
def profile():
    if request.method == 'POST':
        data = request.get_json()
        conn = mysql.connect()
        cur = conn.cursor()
        if data['event'] == 'profile_message':
            try:
                cur.execute('update account set message = %s where id = %s', (data['message'], session['id']))
                cur.commit()
            finally:
                conn.close()
    return render_template('profile.html', time=time.time())

@app.route('/mainmenu', methods=['GET', 'POST'])
@login_required
def mainmenu():
    if request.method == 'POST':
        data = request.get_json()
        conn = mysql.connect()
        cur = conn.cursor()
        if data['request'] == 'home':
            try:
                cur.execute('''select r.id1, r.id2, a1.nickname, a2.nickname, a1.message, a2.message
                               from relation r, account a1, account a2
                               where (r.id1 = a1.id and r.id2 = a2.id) 
                                   and (r.id1 = %s)
                                   and relation_type = '2'
                            ''', (session['id'], ))
                result = []
                for x in cur.fetchall():
                    result.append(list(x))
                for x in range(len(result)):
                    result[x].remove(session['id'])
                    result[x].remove(session['nickname'])
                    result[x].remove((session['message']))
                result = sorted(result, key=lambda row : row[1])
            finally:
                conn.close()

            html = '''
                        <div class="friend-list" style="width: 100%; height : 7vh; border: 1px solid white;" onclick="request_function({0}, 'profile_window')" ondblclick="enter_chat('{1}')">
                            <div style="width:30%; float: left;">
                                <img src="/static/profile/{1}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" style="width:calc(7vh - 2px); height:calc(7vh - 2px); float: left;">
                                <p>{2}</p>
                            </div>
                            <div style="width:70%; float: left;">
                                <p>{3}</p>
                            </div>
                       </div><hr>
                   '''.format("{{'request':'load_profile', id : '{0}'}}".format(session['id']), session['id'], session['nickname'], '나에게 보내기')
            for x in result:
                html += '''
                        <div class="friend-list" style="width: 100%; height : 7vh; border: 1px solid white;" onclick="request_function({0}, 'profile_window')" ondblclick="enter_chat('{1}')">
                            <div style="width:30%; float: left;">
                                <img src="/static/profile/{1}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" style="width:calc(7vh - 2px); height:calc(7vh - 2px); float: left;">
                                <p>{2}</p>
                            </div>
                            <div style="width:70%; float: left;">
                                <p>{3}</p>
                            </div>
                       </div>
                   '''.format("{{'request':'load_profile', id : '{0}'}}".format(x[0]), x[0], x[1], x[2])

            return html

        if data['request'] == 'personal_chat_list':
            try:
                cur.execute('''select if(p.id1 < p.id2, concat(p.id1, ' ', p.id2), concat(p.id2, ' ', p.id1)) room,
                                      a1.nickname, a2.nickname, 
                                      latest_message(p.id1, p.id2), 
                                      max(p.date)
                                from personal_chatting p, account a1, account a2
                                where (id1 = '{0}' or id2 = '{0}') and a1.id = p.id1 and a2.id = p.id2
                                group by room
                                order by date'''.format(session['id']))
                result = []
                for x in cur.fetchall():
                    result.append(list(x))
            finally:
                conn.close()
            for x in result:
                a = x[0].split(' ')
                a.remove(session['id'])
                x.remove(session['nickname'])
                x[0] = a[0]

            html = ''

            for x in result:
                html = html + '''
                        <div class="friend-list" style="width: 100%; height : 7vh; border: 1px solid white;" onclick="request_function({0}, 'profile_window')" ondblclick="enter_chat('{1}')">
                            <div style="width:30%; float: left;">
                                <img src="/static/profile/{1}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" style="width:calc(7vh - 2px); height:calc(7vh - 2px); float: left;">
                                <p>{2}</p>
                            </div>
                            <div style="width:70%; float: left;">
                                <p>{3}</p>
                            </div>
                       </div>
                   '''.format("{{'request':'load_profile', 'id':'{0}'}}".format(x[0]), x[0], x[1], x[2])

            return html

        if data['request'] == 'request_view':
            try:
                cur.execute('''select r.id1, r.id2, a1.nickname, a2.nickname
                               from relation r, account a1, account a2
                               where (r.id1 = a1.id and r.id2 = a2.id) 
                                   and (r.id1 = %s or r.id2 = %s) 
                                   and relation_type = '0'
                            ''', (session['id'], session['id']))
                result = []
                for x in cur.fetchall():
                    result.append(list(x))
                for x in range(len(result)):
                    result[x].remove(session['id'])
                    result[x].remove(session['nickname'])
                result.sort()
                html = ''
                for x in result:
                    html = html + '''
                            <div class="friend-list" style="width: 100%; height : 7vh; border: 1px solid white;" onclick="request_function();">
                                <div style="width:70%; float: left;">
                                    <img src="/static/profile/{0}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" style="width:calc(7vh - 2px); height:calc(7vh - 2px); float: left;">
                                    <p>{1}</p>
                                </div>
                                <div style="width:30%; float: left;">
                                    <button onclick="">수락</button>
                                    <button onclick="">차단</button>
                                    <button onclick="">취소</button>
                                </div>
                           </div>
                       '''.format(x[0], x[1])
            finally:
                conn.close()
            try:
                return html
            except:
                return 0

        if data['request'] == 'find_friend':
            try:
                cur.execute('''
                            select a.id, a.nickname, a.message, case when num is null then null else num end number
                            from account a, (select max(relation_type) num from relation where (id1 = '{0}' and id2 = '{1}') or (id1 = '{1}' and id2 = '{0}')) b
                            where a.id = '{0}'

                            '''.format(data['id'], session['id']))
                result = cur.fetchone()
            finally:
                conn.close()

            if result:
                return '''<div id = "friend_box" style = "width:calc(100vw - 81px); float: left; margin-top : 40px">\
                            <table class = "table table-striped" style="text-align: center">\
                                <tr>\
                                    <th style ="width:15%"> 사용자명 </th>\
                                    <th style ="width:15%"> 아이디 </th>\
                                    <th style ="width:40%"> 프로필 메세지 </th>\
                                    <th style ="width:30%"> 친구 요청 </th>\
                                </tr>\
                                <tr>\
                                    <td> <img src = "/static/profile/{1}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" style="width: 40px; height: 40px; margin-right: 5px"> {0} </td>\
                                    <td> {1} </td>\
                                    <td> {2} </td>\
                                    <td id="status"> {3} <td>\
                                </tr>\
                            </table>\
                        </div>'''.format(result[1], result[0], result[2], (lambda : '''<button onclick="request_friend('{0}');">요청</button>'''.format(result[0]) if (result[3] == None) else '''<p>요청 완료</p>''')())
            else:
                return '<h2>결과가 없습니다.</h2>'

        if data['request'] == 'request_friend':
            try:
                cur.execute('select id1, id2, relation_type from relation where (id1 = %s and id2 = %s) or (id1 = %s and id2 = %s)',
                            (session['id'], data['id'], data['id'], session['id']))
                result = cur.fetchone()
                if not result:
                    cur.execute('insert into relation (id1, id2, relation_type) values (%s, %s, %s)',
                                (session['id'], data['id'], 1))
                #else:
                    #if result[2] == '0':

                    #if result[2] == '1':




                conn.commit()
            finally:
                conn.close()

            return '1'

        if data['request'] == 'make_group':
            group_number = generate_number()
            channel_number = generate_number()
            room_number = generate_number()
            try:
                cur.execute('insert into treechat.group values (%s, %s, %s)',
                            (group_number, session['id'], data['name']))
                cur.execute("insert into member values (%s, %s, %s)", (group_number, session['id'], 0))
                cur.execute("insert into number_log values (%s)", group_number)
                cur.execute("insert into channel values (%s, %s, %s, %s, %s, %s)",
                            (channel_number, group_number, data['name'], session['id'], None, 0))

                cur.execute("insert into number_log values (%s)", channel_number)
                cur.execute("insert into room values (%s, %s, %s, %s)", (room_number, channel_number, '공지', 0))
                cur.execute("insert into number_log values (%s)", room_number)
                conn.commit()
            finally:
                conn.close()

            return jsonify(group_number = group_number, channel_number=channel_number)

        if data['request'] == 'group_list':
            html = ''
            try:
                cur.execute('''select m.group_num, m.id, g.group_name, m.permission_level
                            from treechat.member m, treechat.group g
                            where m.group_num = g.group_num and m.id = %s''', (session['id']))
            finally:
                conn.close()

            for x in cur.fetchall():
                html = html + '''
                <div class ="friend-list" style="width: 100%; height : 7vh; border: 1px solid white;" onclick="request_function({0}, 'channel_window', make_info);">
                    <div style = "width:30%; float: left;"> 
                        <img src = "/static/profile/{1}_profile.png" onerror = "if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" style = "width:calc(7vh - 2px); height:calc(7vh - 2px); float: left;">
                        <h4>{2}</h4>
                    </div>
                    <div style = "width:70%; float: left;">
                        <h4>대화 내용</h4>
                    </div>
                </div>'''.format({'request':'load_group_info', 'group_num': x[0]}, x[1], x[2])
            return html

        if data['request'] == 'load_channel_tree':
            pass

        if data['request'] == 'load_profile':
            try:
                cur.execute('select nickname, message from account where id = %s', (data['id'], ))
            finally:
                conn.close()

            result = cur.fetchone()
            return '''
                <div id="profile_div" style="float:left; margin-left:calc(50% - 25vw / 2); margin-top:calc(50% - (3em + 25vw + 10vh) / 2)">
                    <div id="pic" style="width: 25vw; height:25vw">
                        <img id="profile_picture" src="/static/profile/{0}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" alt="Profile Picture" style="width:100%; height:100%">
                    </div>
                    <div style="color: white; width: 25vw;">
                        <p>아이디 : {0}</p>
                        <p>닉네임 : {1}</p>
                        <p>상태 메세지</p>
                        <textarea style="width: 25vw; height: 10vh; resize:none;" disabled>{2}</textarea>
                    </div>
                </div>'''.format(data['id'], result[0], result[1])

        if data['request'] == 'load_group_info':
            try:
                cur.execute('select group_num, group_name from treechat.group where group_num = %s', (data['group_num'], ))
                result1 = cur.fetchone()
                cur.execute('select channel_num, channel_name, Upper_channel, group_num from channel where group_num = %s', data['group_num'])
                result2 = []
                for x in cur.fetchall():
                    result2.append(list(x))
            finally:
                conn.close()

            root = dictionary(channel_num=None, name=None, parent=None, group_num=None, child=[])
            root.insert_node(result2)

            return json.dumps((root, result1), ensure_ascii=False)

        if data['request'] == 'asdf':
            pass

        if data['request'] == 'accept_friend':
            try:
                cur.execute('''update treechat.relation set relation_type = 1 where ''')
            finally:
                conn.close()

        if data['request'] == 'cancel':
            pass

    return render_template('mainmenu.html', time=time.time())

@app.route('/personal_chat/<id>')
@login_required
def personal_chat(id):
    conn = mysql.connect()
    cur = conn.cursor()
    try:
        cur.execute('''select p.personal_number, p.id1, p.id2, p.contents, date_format(p.date, "%T"), a.nickname 
                       from personal_chatting p, account a 
                       where p.id1 = a.id and ((id1 = '{0}' and id2 = '{1}') or (id1 = '{1}' and id2 = '{0}'))'''.format(session['id'], id))
        result = []
        for x in cur.fetchall():
            result.append(list(x))

        for x in result:
           x[3] = Markup(x[3].replace('\n', '<br>'))

    finally:
        conn.close()
    return render_template('personal_chat.html', receiver = id, log=result, time=time.time())

@app.route('/group/<int:groupnum>/<int:channelnum>', methods=['GET', 'POST'])
@login_required
def groupchat(groupnum, channelnum):
    conn = mysql.connect()
    cur = conn.cursor()
    if request.method == 'POST':
        data = request.get_json()
        if data['event'] == 'make_channel':
            try:
                channel_num = generate_number()
                cur.execute('''insert into channel values (%s,%s,%s,%s,%s,%s)''',
                            (channel_num, groupnum, data['name'], session['id'], channelnum, 0))
                room_num = generate_number()
                cur.execute('''insert into room values (%s,%s,%s,%s)''', (room_num, channel_num, '공지', 0))
                print( channel_num, room_num)
                cur.execute('''insert into number_log values (%s)''', (channel_num, ))
                cur.execute('''insert into number_log values (%s)''', (room_num,))
                conn.commit()
            finally:
                conn.close()

            return jsonify()

        if data['event'] == 'make_room':
            try:
                room_num = generate_number()
                cur.execute('''select max(location) from room where channel_num = %s''', (channelnum, ))
                max_location = cur.fetchone()
                cur.execute('''insert into room values (%s,%s,%s,%s)''', (room_num, channelnum, data['name'], max_location[0]+1))
                cur.execute('''insert into number_log values (%s)''', (room_num, ))
                conn.commit()
            finally:
                conn.close()

            return jsonify()

        if data['event'] == 'room_select':
            try:
                cur.execute('''select r.log_number, r.room_number, a.nickname, r.contents, r.date 
                                from room_log r, account a
                                where r.id = a.id ''')
            finally:
                conn.close()

        if data['event'] == 'list':
            try:
                cur.execute('select channel_num, channel_name, Upper_channel, group_num from channel where group_num = %s', (groupnum, ))
                channel_list = []
                for x in cur.fetchall():
                    channel_list.append(list(x))
                channel_dict = dictionary(channel_num = None, name = None, group_num = None, child = [])
                channel_dict.insert_node(channel_list.copy())

                cur.execute('select room_number, room_name, location from room where channel_num = %s order by location', (channelnum, ))
                room_list = cur.fetchall()
                html = ''
                for x in room_list:
                    if x[2] == 0:
                        html += '''
                            <ul>
                                <span class="channel_node" style="font-size: 1.3em;" onclick="enter_room(this, {0}, '{1}'); change_notice_mod(1);">{2}</span>
                            </ul>
                            '''.format({'event': 'load_message', 'value': '{0}'.format(x[0])}, 'message_window', x[1])
                    else:
                        html += '''
                            <ul>
                                <span class="channel_node" style="font-size: 1.3em;" onclick="enter_room(this, {0}, '{1}'); change_notice_mod(0);">{2}</span>
                            </ul>
                            '''.format({'event': 'load_message', 'value': '{0}'.format(x[0])}, 'message_window', x[1])
            finally:
                conn.close()

            return json.dumps((channel_dict, html), ensure_ascii=False)

        if data['event'] == 'load_message':
            try:
                cur.execute('''select r.log_number, r.id, a.nickname, r.contents, r.date
                               from room_log as r left join account as a on r.id = a.id
                               where room_number = {0}
                               order by date'''.format(data['value']))
                result = cur.fetchall()

            finally:
                conn.close()
            html = ''
            for x in result:
                if x[1] == session['id']:
                    html += '''
                        <div align="right" style="color: white;">
                            <span style="margin: 0px;">{time}</span>
                            <div class="balloon2" style="color : white; max-width: 40vw;">{message}</div>
                        </div>
                    '''.format(time = x[4], message = x[3].replace('\n', '<br>'))
                else:
                    html += '''
                        <div align="left" style="color: white;">
                            <img style="width:30px; height:30px;" src="/static/profile/{sender}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';">
                            <span>{sender}</span><br>
                            <div class="balloon1" style="color : white">
                                <span>{message}</span>
                            </div>
                            <span>{time}</span>
                        </div>
                    '''.format(sender = x[1], message = x[3].replace('\n', '<br>'), time = x[4])

            return html

        if data['event'] == 'search_group_chat':
            print(data['value'])

            return jsonify()

        if data['event'] == 'file':
            pass

        if data['event'] == 'picture':
            pass

    try:
        cur.execute('''select channel_name from channel where channel_num = %s''', (channelnum))
        channel_name = cur.fetchone()
        cur.execute('''select * from room where channel_num = %s''', (channelnum, ))
        room_list = cur.fetchall()
        cur.execute('''select m.id, a.nickname from member as m left join account as a on m.id = a.id where m.group_num = %s''', (groupnum))
        member_list = cur.fetchall()
    finally:
        conn.close()

    return render_template('chatting_channel.html', time=time.time(), groupnum=groupnum,
                           channelnum=channelnum, room_list=room_list, member_list=member_list,
                           channel_name = channel_name[0], session_id = session['id'])

@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('email', None)
    session.pop('nickname', None)
    session.pop('message', None)
    return redirect('/')

@app.route('/notice')
def notice():
    return render_template('notice.html', time=time.time())

@app.route('/phone')
def phone_room():
    return render_template('basic_audio_call.html', time=time.time())

################################################################################
@socketio.on('join_room')
def on_join(data):
    join_room(data['room'])

@socketio.on('leave_room')
def on_leave(data):
    leave_room(data['room'])

@socketio.on('login')
def on_login(data):
    join_room(session['id']+'_mainmenu')

@socketio.on('send_personal_message')
def send_personal_message(message):
    conn = mysql.connect()
    cur = conn.cursor()
    print(message['message'])
    try:
        if message['message'] not in ['\n', '']:
            cur.execute('insert into personal_chatting (id1, id2, contents, date) values (%s, %s, %s, now())', (session['id'], message['receiver'], message['message']))
            message['message'] = message['message'].replace('\n', '<br>')
            conn.commit()
        else:
            print('asdf')
    finally:
        conn.close()
    for x in set([session['id'], message['receiver']]):
        print(x)
        socketio.emit('receive_personal_message', { 'message' : message['message'], 'sender' : session['id'], 'nickname': session['nickname'] } , room=x)

@socketio.on('send_message')
def send_message(message):
    conn = mysql.connect()
    cur = conn.cursor()
    try:
        cur.execute('''insert into room_log (room_number, id, contents, date) values (%s,%s,%s,now())'''
                    , (message['room'].split('/')[-1], message['sender'], message['message']))
        conn.commit()
    finally:
        conn.close()
    socketio.emit('receive_message', {'message': message['message'], 'sender': session['id'], 'nickname': session['nickname']}, room=message['room'])

@socketio.on('send_notice_message')
def send_group_message(message):
    conn = mysql.connect()
    cur = conn.cursor()
    try:
        cur.execute('select channel_num, channel_name, Upper_channel, group_num from channel where group_num = %s',
                    message['group_num'])

        result2 = []
        for x in cur.fetchall():
            result2.append(list(x))

        root = dictionary(channel_num=None, name=None, parent=None, group_num=None, child=[])
        root.insert_node(result2)
        cur.execute('''select c.channel_num, r.room_number
                       from room r, channel c
                       where r.channel_num = c.channel_num 
                           and r.location = '0' 
                           and c.group_num = %s''', (message['group_num']))
        notice_list = cur.fetchall()

        under_channel = root.print_under_target(data=root.search(int(message['channel_num'])))

        room_list = []
        for x in under_channel:
            for y in notice_list:
                if x == y[0]:
                    room_list.append(y[1])
                    break

        for x in room_list:
            cur.execute('''insert into room_log (room_number, id, contents, date) values (%s,%s,%s,now())''', (x, session['id'], message['message']))

        conn.commit()
    finally:
        conn.close()

    socketio.emit('receive_message', {'message': message['message'], 'room': message['room'], 'sender': session['id'], 'nickname': session['nickname']}, room=message['room'])

if __name__ == "__main__":
    socketio.run(app, host = "203.252.231.149", port=80, debug=True)
