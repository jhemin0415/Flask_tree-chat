import os

subscription_info = {"endpoint":"https://fcm.googleapis.com/fcm/send/d3JKsdh_ZJI:APA91bGNJ1310rEEoC_s9FIY3WVz72sUJXn9GIKgiV29-D8awAj3hi6dY3HCj_hJG21vPf9L0yo-pwdbVwneY83vXKuUs3RcWfdotSkfddbMZiQyAhtp2r2lDnuIVYVASDrBkjLqVDtX","expirationTime":None,"keys":{"p256dh":"BC0TJgvDYKnRbHaU_9KUUw605Dd_WkN-9dvU64Sd80jUkSnhVcm6vlT0_1nExVkU-RvQE8ziQnnRB57rytMtyQI","auth":"JWOvi464krLeqtzLAf8hyg"}}

endpoint = subscription_info['endpoint']
p256dh = subscription_info['keys']['p256dh']
auth = subscription_info['keys']['auth']

os.system('''curl -d "endpoint={0}&p256dh={1}&auth={2}&data={3}" http://127.0.0.1:8080 '''.format(subscription_info['endpoint'], subscription_info['keys']['p256dh'], subscription_info['keys']['auth'], 'hello glitch.'))