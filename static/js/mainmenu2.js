'use strict';

const applicationServerPublicKey = 'BNHwyAocBXYnv2booHfhG014j0QVayVK4zhY5_JGRyNh8aUddUMjrRbAs8IQezJVpnJgOmwq9SQfDPbS1Hi6rdI';
let isSubscribed = false;
let swRegistration = null;


if ('serviceWorker' in navigator && 'PushManager' in window) {
    console.log('Service Worker and Push is supported');
  
    navigator.serviceWorker.register('static/js/sw.js')
    .then(function(swReg) {
      console.log('Service Worker is registered', swReg);
  
      swRegistration = swReg;
      subscribeUser();
    })
    .catch(function(error) {
      console.error('Service Worker Error', error);
    });
  } else {
    console.warn('Push messaging is not supported');
    pushButton.textContent = 'Push Not Supported';
  }

  function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');
  
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
  
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
  
  

  function subscribeUser() {
    const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
    swRegistration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey
    })
    .then(function(subscription) {
      console.log('User is subscribed.');
      var xhr = new XMLHttpRequest();
      xml.open('POST', '/send_subscribe', true);
      xml.setRequestHeader('content-type', "application/json;charset=UTF-8");
      xml.onreadystatechange = function(){
        if (xml.readyState == 4 && xml.status == 200){
            
        }
        
    }

      xml.send(JSON.stringify(subscription));
      isSubscribed = true;
  
      
    })
    .catch(function(err) {
      console.log('Failed to subscribe the user: ', err);
      
    });
  }


  
function unsubscribeUser() {
    swRegistration.pushManager.getSubscription()
    .then(function(subscription) {
      if (subscription) {
        return subscription.unsubscribe();
      }
    })
    .catch(function(error) {
      console.log('Error unsubscribing', error);
    })
    .then(function() {
      updateSubscriptionOnServer(null);
  
      console.log('User is unsubscribed.');
      isSubscribed = false;
  
      updateBtn();
    });
  }
  