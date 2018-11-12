var script = document.getElementsByTagName('script');
var myscript = script[script.length -1];
var queryString = myscript.src.replace(/^[^\?]+\??/,'');
var params = parseQuery(queryString);
var room_base = `${params.groupnum}/${params.channelnum}`;
var room_name = null;
var socket = io.connect('http://203.252.231.149');
var notice = false;

console.log(params.session);
function enter_room(element, value, elmid){
    console.log(value.value);
    xml = new XMLHttpRequest();
    xml.open('POST', '#', true);
    xml.setRequestHeader('content-type', 'application/json;charset=UTF-8');
    xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            document.getElementById(elmid).innerHTML = xml.response;
            socket.emit('leave_room', {'room': room_name});
            room_name = `${room_base}/${value.value}`;
            document.getElementById('join_room_name').innerHTML = `<h4>${element.innerText}</h4>`
            socket.emit('join_room', {'room': room_name});
            document.getElementById('message_area').disabled = false;
        }
    }
    xml.send(JSON.stringify(value));
}

socket.on('receive_message', function(message){
    var message_window = document.getElementById('message_window');
    message.message = message.message.replace('/\n/gi');
    var d = new Date();
    if(message.sender == params.session){
        message_window.innerHTML += `
            <div align="right" style="color: white;">
                <span style="margin: 0px;">${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}</span>
                <div class="balloon2" style="color : white; max-width: 40vw;">${message.message}</div>
            </div>`;
    }
    else{
        message_window.innerHTML += `
            <div align="left" style="color: white;">
                <img style="width:30px; height:30px;" src="/static/profile/${message.sender}_profile.png" onerror="if (this.src != 'error.jpg') this.src = '/static/profile/default_profile.png';">
                <span>${message.nickname}</span><br>
                <div class="balloon1" style="color : white">
                    <span>${message.message}</span>
                </div>
                <span>${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}</span>
            </div>`;
    }
    message_window.scrollTo(0,message_window.scrollHeight);
})

function send_message(){
    
    var message = document.getElementById('message_area');
    if (notice == false){
        socket.emit('send_message', {'message':message.value, 
                                     'room' : room_name, 
                                     'sender' : params.session});
    }
    else{
        socket.emit('send_notice_message', {'message':message.value, 
                                            'room' : room_name,
                                            'sender' : params.session,
                                            'group_num' : params.groupnum,
                                            'channel_num' : params.channelnum});

    }
    message.value = "";
    message.focus();
}

function parseQuery(query){
    var Params = new Object();
    if (!query) return Params;
    var Pairs = query.split(/[;&]/);
    for (var i = 0; i < Pairs.length; i++){
        var keyval = Pairs[i].split('=');
        if (!keyval || keyval.length != 2) continue;
        var key = unescape(keyval[0]);
        var val = unescape(keyval[1]);
        val = val.replace(/\+/g, ' ');
        Params[key] = val;
    }
    return Params
}

function channel_room_list(){
    document.getElementById('function_response').innerHTML = `
        <div>
            <div id="room_window" style="width: 100%; height: calc(60% - 25px); text-align: center">
                <div style="border-bottom: solid 1px white; background-color: #18191c">
                    <h4>채널</h4>
                </div>
                <div id="channel_list" style="width: 100%; height: calc(100% - 36px - 26px); text-align: left">
                    <ul class="tree" id="root"></ul>
                </div>
                <div class="plus_button" style="border-bottom: solid 1px white; border-top: solid 1px white;" data-toggle="modal" data-target="#plus_channel">
                    <p>채널 추가</p>
                </div>
            </div>
            <div id="room_window" style="width: 100%; height: calc(40% - 25px); text-align: center">
                <div style="border-bottom: solid 1px white; border-top: solid 1px white; background-color: #18191c">
                    <h4>방 목록</h4>
                </div>
                <div id="room_list" style="width: 100%; height: calc(100% - 36px - 26px); text-align: left">

                </div>
                <div class="plus_button" style="border-bottom: solid 1px white; border-top: solid 1px white;" data-toggle="modal" data-target="#plus_room">
                    <p>방 추가</p>
                </div>
            </div>
            <div id="audio_control" style="top: calc(100% - 50px); width: 100%; heightbackground-color: #18191C">
                <div style="width: 100%">
                    <div id="output_control" style="float:left">
                        <img class="audio_controler" src="/static/headphone-symbol.png">
                    </div>
                    <div id="input_control" style="float:left">
                        <img class="audio_controler" src="/static/microphone-black-shape.png">
                    </div>
                    <div id="connect_control" style="float:left">
                        <img class="audio_controler" src="/static/no-phone.png">
                    </div>
                </div>
            </div>  
        </div>
    `;
    get_channel_room();

}

function search_message(){
    document.getElementById('function_response').innerHTML = `
        <div style="text-align: center">
            <h4>검색</h4>
        </div>
        <div>
            <input type="text" placeholder="메시지" style="width: 100%" oninput="request_function({'event': 'search_group_chat', 'value': this.value}, 'search_result')">
        </div>
        <div id="search_result">

        </div>
    `
}

function get_channel_room(){
    xml = new XMLHttpRequest();
    xml.open('POST', '#', true);
    xml.setRequestHeader('content-type', 'application/json;charset=UTF-8');
    xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            var response = JSON.parse(xml.response);
            console.log(response);
            make_channel(response[0], 1);
            document.getElementById('room_list').innerHTML = response[1];
        }        
    }
    xml.send(JSON.stringify({'event':'list'}));
}

function make_channel(data, step, elmntid){
    if (elmntid == undefined){
        elmntid = 'root';
    }
    
    if (elmntid == 'root'){
    document.getElementById(`${elmntid}`).innerHTML += `
        <li class="root" id="${data.channel_num}">
            <span class="channel_node" onclick="window.location.href='/group/${data.group_num}/${data.channel_num}';">${data.name}</span>
        </li>
        `;
    }
    else{
        document.getElementById(`${elmntid}`).innerHTML += `
        <li id="${data.channel_num}">
            <span class="channel_node" onclick="window.location.href='/group/${data.group_num}/${data.channel_num}';">${data.name}</span>
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
        make_channel(data.child[index], step, `${data.channel_num}_child`);
        index += 1;
    }
    
}

function make_channel_room(eventname, value){
    xml = new XMLHttpRequest();
    xml.open('POST', '#', true);
    xml.setRequestHeader('content-type', 'application/json;charset=UTF-8');
    xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            window.location.reload();
        }
    }
    xml.send(JSON.stringify({'event':eventname, 'name': value}));

}

window.onload = function(){
    channel_room_list();
    socket.emit('login', {'room': 'a'});
    document.getElementById("message_area").addEventListener("keyup", function(event) {
        event.preventDefault();
        if (event.keyCode === 13) {
            if(event.shiftKey){ 
                send_message();
            }
        }
    });
}

function message_change(el){

}

function change_notice_mod(set){
    if (set == 1){
        notice = true;
    }
    else {
        notice = false
    }
}

function on_dragover(e){
    console.log(1);
    document.getElementById('message_window').style.cursor = "copy";
}