function sendForm(e){
  e.preventDefault();
  var xml = new XMLHttpRequest();
  xml.open('POST', '/', true);
  xml.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xml.send(JSON.stringify({'id' : document.getElementById('Username').value, 'password' : document.getElementById('Password').value}));
  xml.onreadystatechange = function(aEvt){
    if (xml.readyState == 4){
      response = JSON.parse(xml.response);
      if (response['success'] == '1'){
        window.location.href = '/mainmenu';
      }
    }
  };

}

function registerForm(e){
  var xml = new XMLHttpRequest();
  xml.open('POST', '/register', true);
  xml.onreadystatechange = function(aEvt){
    if (xml.readyState == 4){
      response = JSON.parse(xml.response);
      if (response.event == 'success'){
        alert('회원가입이 정상적으로 처리되었습니다.');
        window.location.href = '/';
      }
      if (response.event == 'id_overlap'){
        alert('아이디가 중복되었습니다.');
        
      }
      if (response.event == 'email_overlap'){
        alert('이메일이 중복되었습니다.');
        
      }
    }
  };
  xml.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xml.send(JSON.stringify({'id' : document.getElementById('reg_Username').value, 
                           'password' : document.getElementById('reg_Password').value, 
                           'email' : document.getElementById('reg_Email').value
                          }));

}

