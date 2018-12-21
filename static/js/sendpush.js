function getDetails() {
    const details = window.localStorage.getItem('last-known-details');
    try {
      if (details) {
        return JSON.parse(details);
      }
    } catch (err) {
      // NOOP
    }
    return null;
  }

function saveDetails(details) {
    window.localStorage.setItem('last-known-details',
      JSON.stringify(details));
  }

function sendPushMessage() {
    const textToSendTextArea = 'this is glitch';
    const subscriptionString = `{"endpoint":"https://fcm.googleapis.com/fcm/send/drdwVHYI678:APA91bHPHsSEGd64d8QdgsLPOrsD5Pl2En-SKXRxtES8Nm99g_Fd_RNlViiiCEu_USfarMe1Q0_CVvm-pnvVMs5FHwjaspzvrqGJXUxufGyfkq7STpSUNqKoDGFUyan-4nGl1T61JLrq","expirationTime":null,"keys":{"p256dh":"BMyB0MQKqS67zzFEYf_FdAHv5NHP8q7y_SIh1nsP2nm_bp-LcqLCBPD_U7CaKw2d6ok4-tono8cZM_0j0Z7G5cI","auth":"tjgXOxAXLZwX89UdfMEVHw"}}`;
    const dataString = textToSendTextArea;
  
    if (subscriptionString.length === 0 ) {
      return Promise.reject(new Error('Please provide a push subscription.'));
    }
  
    let subscriptionObject = null;
    try {
      subscriptionObject = JSON.parse(subscriptionString);
    } catch (err) {
      return Promise.reject(new Error('Unable to parse subscription as JSON'));
    }
  
    if (!subscriptionObject.endpoint) {
      return Promise.reject(new Error('The subscription MUST have an endpoint'));
    }
  
    if (subscriptionObject.endpoint.indexOf('…') !== -1) {
      return Promise.reject(new Error('The subscription endpoint appears to be ' +
        'truncated (It has \'...\' in it).\n\nDid you copy it from the console ' +
        'in Chrome?')
      );
    }
  
    

    const privateElement = document.querySelector('.js-private-key');
  
    return fetch('https://web-push-codelab.glitch.me/api/send-push-msg', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        subscription: subscriptionObject,
        data: dataString,
        applicationKeys: {
          public: 'BMoj5YTNOIb0uXz6Q0GGVFdVrirHJF-etr9SY3YHz6MNNa0f_QF3SG-yLTg63YGDqKqN87aBewlNC6owGqAr31A',
          private: 'yr017fZJFt_8L5ks6MHDqsPODpiuh5-oh11tdLs5oO4',
        }
      })
    })
    .then((response) => {
      if (response.status !== 200) {
        return response.text()
        .then((responseText) => {
          throw new Error(responseText);
        });
      }
    });
  }

sendPushMessage()