from pywebpush import webpush, WebPushException

try:
    webpush(
        subscription_info={
            "endpoint": "https://push.example.com/v1/12345",
            "keys": {
                "p256dh": "0123abcde...",
                "auth": "abc123..."
            }},
        data="Mary had a little lamb, with a nice mint jelly",
        vapid_private_key="path/to/vapid_private.pem",
        vapid_claims={
                "sub": "mailto:YourNameHere@example.org",
            }
    )
except WebPushException as ex:
    print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
    # Mozilla returns additional information in the body of the response.
    if ex.response and ex.response.json():
        extra = ex.response.json()
        print("Remote service replied with a {}:{}, {}",
              extra.code,
              extra.errno,
              extra.message
              )