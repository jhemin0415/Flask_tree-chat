var socket = io.connect("http://127.0.0.1");

function home(){
    document.getElementById('main').innerHTML = `
        <div id = "friend_window" class="container" style="width:calc(50vw - 45px); height:calc(100vh - 56px); border-right:1px solid white; float: left; padding: 0px;">
            <ul class="nav nav-pills" role="tablist">
                <li class="nav-item">
                    <a class="nav-link active" id="personal_chat_list" data-toggle="pill" href="#menu1" onclick="request_function({'request':'home'}, 'menu1');">친구</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="request_list" data-toggle="pill" href="#menu3" onclick="request_function({'request':request_view'}, 'menu3');">요청</a>
                </li>
            </ul>

            <div class="tab-content">
                <div id="menu1" class="container tab-pane active" style="padding:0px;">
                </div>
                <div id="menu3" class="container tab-pane fade" style="padding:0px;" onclick="">
                </div>
            </div>  
        </div>

        <div id="profile_window" class="container" style="width:calc(50vw - 45px); height:calc(100vh - 56px); float: left; padding: 0px;">

        </div>`;
    request_function({'request':'home'}, 'menu1');
    
}

//toolbar personal_chat
function recent_chat(){
    document.getElementById('main').innerHTML = `
        <div class="container" style="width:calc(50vw - 45px); height:calc(100vh - 56px); border-right:1px solid white; float: left; padding: 0px;">
            <div id="menu1" class="container tab-pane active" style="padding:0px;">
            </div>

        </div>

        <div id="profile_window" class="container" style="width:calc(50vw - 45px); height:calc(100vh - 56px); float: left; padding: 0px;">

        </div>`;
    request_function({'request':'personal_chat_list'}, 'menu1');
    
}

//toolbar group_chat
function group_list(){
    document.getElementById('main').innerHTML = `
        <div id="group_window"class="container" style="width:calc(50vw - 45px); height:calc(100vh - 56px); border-right:1px solid white; float: left; padding: 0px;">
        </div>
        <div id="channel_window" class="container" style="width:calc(50vw - 45px); height:calc(100vh - 56px); float: left; padding: 0px;">
        </div>`;
    request_function({'request':'group_list'}, 'group_window');
    
}

//toolbar search_user
function search_user(){
    document.getElementById('main').innerHTML = 
    `    <div class="mainbox" id="mainbox">
            <div style="width:calc(100vw - 80px); height:calc(100vh - 56px); float: left; text-align: center">
                <div style="margin-top:100px">
                    <h1>친구 추가</h1>
                    <div style="margin-top:70px">
                        <span>사용자 ID : </span>
                        <input id="friend_name" type="text" placeholder="사용자 ID를 입력해주세요." style="width: 500px">
                        <button onclick="request_function({'request':'find_friend', 'id':document.getElementById('friend_name').value}, 'friend_box')">검색</button>
                    </div>
                </div>
                <div id = "friend_box" style="width:calc(100vw - 81px); float: left; margin-top : 40px">

                </div>
            </div>
        </div>`;
}

//toolbar search_log
function search_chat(){
    document.getElementById('main').innerHTML = `    
        <div class="mainbox" id="mainbox">
            <div style="width:calc(100vw - 80px); height:calc(100vh - 56px); float: left; text-align: center">
                <div style="margin-top : 50px">
                    <h2>내용 검색</h2><br>
                    <span>내용 : </span><input type="text" style="width : 500px" onchange="search_active(this)">
                </div>
            </div>
        </div>`
}

//toolbar make_group
function make_join_group(){
    document.getElementById('main').innerHTML = 
    `   <div class="mainbox" id="mainbox">
            <div style="width:calc(50vw - 40px); height:calc(100vh - 56px) ; float: left;">
                <div style="text-align: center; margin-top:100px">
                    <h1>그룹 만들기</h1>
                        <div style="margin-top:100px">
                            <h3>원하는 그룹의 이름을 써주세요.</h3>
                            <div style="margin-top:50px">
                                <h3>그룹 사진</h3>
                                <img src="/static/plus-button.png"><br>
                                <button>사진 변경</button>
                            </div>
                            <div style="margin-top : 50px">
                                <input id="make_group_name" type="text" placeholder="이름을 입력해 주세요">
                                <button onclick="make_group();">만들기</button>
                            </div>
                        </div>
                    </div>    
                </div>
                <div style="width:calc(50vw - 40px); height:calc(100vh - 56px) ; float: left;">
                    <div style="text-align: center; margin-top: 100px">
                        <h1>그룹 참여하기</h1>
                            <div style="margin-top : 100px">
                            <h3>초대 URL을 입력해주세요.</h3>
                            <div style="margin-top:50px">
                                <img src="/static/network.png" width="200px" height="200px">
                            </div>
                        <div style="margin-top : 50px">
                            <input id="join_group_code" type="text" placeholder="코드를 입력해 주세요">
                            <button>입장</button>
                        </div>
                    </div>                
                </div>
            </div>
        </div>`;
}

function request_function(value, elmid, func){
    xml = new XMLHttpRequest();
    xml.open('POST', '#', true);
    xml.setRequestHeader('content-type', 'application/json;charset=UTF-8');
    xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            var a = xml.response;
            if (func == undefined){
                document.getElementById(elmid).innerHTML = xml.response;
            }
            else{
                
                a = JSON.parse(a);
                func(a, elmid);
            }
        }
    }
    xml.send(JSON.stringify(value));
}

function search_active(elm){
    xml = new XMLHttpRequest();
    xml.open('/mainmenu', true)
    xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            //display result
        }
        
    }
    xml.setRequestHeader('content-type', "application/json;charset=UTF-8");
    xml.send(JSON.stringify({'request' : ''}));

}

function request_friend(id){
    var xml = new XMLHttpRequest();
    xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            alert('요청을 전송했습니다.')
            document.getElementById('status').innerHTML=`
                <p>요청중</P>
            `
        }
    }
    xml.open('POST', 'http://203.252.231.149/mainmenu', false);
    xml.setRequestHeader('content-type', "application/json;charset=UTF-8");
    xml.send(JSON.stringify({'request' : 'request_friend', 'id' : id}));
}

function enter_chat(id){
    var popUrl = "/personal_chat/" + id;
    var popOption = "width=500px, height=700px, resizable=no, scrollbars=no, status=no, location=no;"
    window.open(popUrl, id, popOption);
}

function make_group(){
    var xml = new XMLHttpRequest();
    xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            var response = JSON.parse(xml.response)
            window.location.href=`/group/${response.group_number}/${response.channel_number}`
        }
    }
    xml.open('POST', 'http://203.252.231.149/mainmenu', false);
    xml.setRequestHeader('content-type', "application/json;charset=UTF-8");
    xml.send(JSON.stringify({ 'request' : 'make_group', "name" : document.getElementById('make_group_name').value }));
}

function make_info(data, elementId){
    document.getElementById(elementId).innerHTML = 
    `
    <div id="group_pic" style="width:20vh; height:20vh">
        <img  id="profile_picture" src="/static/profile/${data.channel_num}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';" alt="Profile Picture" style="width:100%; height:100%; margin-left: 12.5vw">
    </div>
    <hr style="background-color: white">
    <div id="channel_list">
        <li class="tree" id="root">
        </li>
    </div>
    `
    
    make_tree(data[0]);
}

function make_tree(data, elmntid){
    if (elmntid == undefined){
        elmntid = 'root';
    }
    
    if (elmntid == 'root'){
    document.getElementById(`${elmntid}`).innerHTML += `
        <li class="root" id="${data.channel_num}">
            <span style="" onclick="window.location.href='/group/${data.group_num}/${data.channel_num}';">${data.name}</span>
        </li>
        `;
    }
    else{
        document.getElementById(`${elmntid}`).innerHTML += `
        <li id="${data.channel_num}">
            <span class="channel_node" style="" onclick="window.location.href='/group/${data.group_num}/${data.channel_num}';">${data.name}</span>
        </li>
        `;        
    }

    if (data.child){
        document.getElementById(`${data.channel_num}`).innerHTML += `
            <ul id="${data.channel_num}_child"></ul>
            `;
    }        
    var index = 0;
    while (index < data.child.length){        
        make_tree(data.child[index], `${data.channel_num}_child`);
        index += 1;
    }
    
}

window.onload = function(){
    home();
    socket.emit('login', 'login');

}


