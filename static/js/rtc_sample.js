var webrtc_capable = true;
var rtc_peer_connection = null;
var rtc_session_description = null
var get_user_media = null;
var connect_stream_to_src = null;
var stun_server = "stun.l.google.com:19302"

connect_stream_to_src = function(media_stream, media_element){
    media_element.srcObject = media_stream;
    media_element.play();
};
