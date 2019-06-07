#!/usr/bin/env python

import os
import re
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from faker import Factory
from twilio.jwt.client import ClientCapabilityToken
from twilio.twiml.voice_response import VoiceResponse, Dial

app = Flask(__name__)
CORS(app)
fake = Factory.create()
alphanumeric_only = re.compile('[\W_]+')
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")

TWILIO_ACCOUNT_SID = 'AC5227a82bd6fc39a05e3151aa98173c04'
TWILIO_AUTH_TOKEN = '3fc271b3fab8aa4cbb2618d1b5565b58'
TWILIO_TWIML_APP_SID = 'AP97b83e5868e74f0ebbf4a24b13a12aec'
TWILIO_CALLER_ID = '4256288664'

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/token', methods=['GET'])
def token():
    print(request.args)
    if request.args.get('identity'):
        identity = request.args.get('identity')
    else:
        identity = alphanumeric_only.sub('', fake.user_name())

    # Create a Capability Token
    capability = ClientCapabilityToken(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    capability.allow_client_outgoing(TWILIO_TWIML_APP_SID)
    capability.allow_client_incoming(identity)
    token = capability.to_jwt()

    # Return token info as JSON
    return jsonify(identity=identity, token=token.decode('utf-8'))


@app.route("/voice", methods=['POST'])
def voice():
    resp = VoiceResponse()
    if "To" in request.form and request.form["To"] != '':
	from_id = TWILIO_CALLER_ID
        if "From" in request.form:
            from_id = request.form["From"][-5:]
        dial = Dial(caller_id=from_id)
        # wrap the phone number or client name in the appropriate TwiML verb
        # by checking if the number given has only digits and format symbols
        if phone_pattern.match(request.form["To"]):
            dial.number(request.form["To"])
        else:
            dial.client(request.form["To"])
        resp.append(dial)
    else:
        resp.say("Thanks for calling!")

    return Response(str(resp), mimetype='text/xml')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
