import logging
import json

from flask import request, Response

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

from testproject.push.__init__ import send_web_push
from testproject.settings.__init__ import VAPID_PUBLIC_KEY

app = FlaskAPI(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

logger = logging.getLogger(__name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription_token = db.Column(db.String(400), unique=True)

    def __init__(self, subscription_token):
        self.subscription_token = subscription_token

    def __repr__(self):
        return "<User %r>" % self.id


@app.route("/subscription/", methods=["GET", "POST"])
def subscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """

    if request.method == "GET":
        return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
                        headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")

    subscription_token = request.get_json("subscription_token")
    return Response(status=201, mimetype="application/json")


@app.route("/push/", methods=["POST"])
def push_to_all_users():
    message = request.get_json("message") if request.data else "Updates available"

    for user in User.query.all():
        try:
            send_web_push(json.loads(user.subscription_token), message)
        except Exception as e:
            logger.error(e)

    return Response(status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)