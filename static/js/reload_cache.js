(function(){

    // Match this timestamp with the release of your code
    var lastVersioning = Date.UTC(2014, 11, 20, 2, 15, 10);
    
    var lastCacheDateTime = localStorage.getItem('lastCacheDatetime');

    if(lastCacheDateTime){
        if(lastVersioning > lastCacheDateTime){
            var reload = true;
        }
    }

    localStorage.setItem('lastCacheDatetime', Date.now());

    if(reload){
        location.reload(true);
    }
    
})();