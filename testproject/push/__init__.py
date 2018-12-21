import logging

from testproject.settings.__init__ import *
from pywebpush import webpush, WebPushException


logger = logging.getLogger(__name__)

def send_web_push(subscription_information, message_body):
    try:
        webpush(
            subscription_info=subscription_information,
            data=message_body,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as exception:
        logger.error(exception)