var script = document.getElementsByTagName('script');
var myscript = script[script.length -1];
var queryString = myscript.src.replace(/^[^\?]+\??/,'');
var params = parseQuery(queryString);

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

var socket = io.connect("http://127.0.0.1");
console.log('connected')

function send_message(){
    var d = new Date();
    var message = document.getElementById('message');
    socket.emit('send_personal_message', {'message':document.getElementById('message').value, 
                                          'sender' : params.session, 
                                          'receiver' : params.receiver });
    message.value = "";
    message.focus();
    console.log('send complete');
}

window.onload = function(){
    var message_window = document.getElementById('message_window')
    socket.emit('join_room', {'room': params.session});
    document.getElementById("message").addEventListener("keyup", function(event) {
        event.preventDefault();
        if (event.keyCode === 13) {
            if(!event.shiftKey){ 
                send_message();
            }

        }
    });

    document.onkeydown = function(e){
        e = e || window.event;
        var escape = false;
        if ('key' in e){
            escape = (e.key == 'Escape' || e.key == "Esc");
        }
        else{
            escape = (e.keyCode == 27);
        }
        if (escape){
            window.close();
        }
    }
    document.getElementById('message_window').scrollTo(0,message_window.scrollHeight);

    message_window.ondragover = function(e){
        e.preventDefault();
        message_window.style.cursor = "copy";
    }

    message_window.ondrop = function(e){
        e.stopPropagation();
        e.preventDefault();
        var file = e.dataTransfer.files[0];
        message_window.style.cursor = "default";
        if (file.size < 20 * 1024 * 1024){
            var filereader = new FileReader();
            filereader.onload = function(){
                socket.emit('send_personal_file', {'event': 'file_upload', 'file': file.name, 'data': filereader.result, 'receiver': params.receiver})
            }
            filereader.readAsText(file);
        }
        

    }
}

socket.on('receive_personal_message', function(message){

    var message_window = document.getElementById('message_window');
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
                <span>${message.sender}</span><br>
                <div class="balloon1" style="color : white">
                    <span>${message.message}</span>
                </div>
                <span>${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}</span>
            </div>`;
    }
    message_window.scrollTo(0,message_window.scrollHeight);
})

socket.on('receive_file', function(message){
    var message_window = document.getElementById('message_window');    



})
