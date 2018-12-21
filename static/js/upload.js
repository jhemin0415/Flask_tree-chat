function file_upload(){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '#', true);
    /*xhr.setRequestHeader('content-type', 'application/json;charset=UTF-8');*/
    xhr.onreadystatechange = function(){
        if (xhr.readyState == 4 && xhr.status == 200){
            window.location.reload();
        }
    }    
    
    xhr.send(document.getElementById('uploadfile').value)
    
    console.log(document.getElementById('uploadfile'));

}