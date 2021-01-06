from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager, get_raw_jwt
import mysql.connector

from resources.doctor import (
    DoctorRegister,
    Doctor,
    DoctorLogin,
    DoctorLogout
    #TokenRefresh,
)
from resources.patient import (
    PatientRegister,
    Patient,
    PatientLogin,
    PatientLogout,
    #TokenRefresh
)
from resources.refresh import TokenRefresh
from blacklist import BLACKLIST

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://root:mysql@localhost:3306/test"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.secret_key = "my_secret_key"
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    user_claims= get_raw_jwt()['user_claims']
    if (
        user_claims['type'] == 'doctor'
    ):  
        return {"type": 'doctor'}
    elif user_claims['type'] == 'patient':
        return {'type': 'patient'}
    else:
        pass

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return (
        jsonify({"description": "The token has expired.", "error": "Token expired"}),
        401,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"description": "Signature verification failed.", "error": "Invalid token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh token required"}
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


# Resources
api.add_resource(DoctorRegister, "/doctor/register")
api.add_resource(Doctor, "/doctor/<int:doctor_id>")
api.add_resource(DoctorLogin, "/doctor/login")
api.add_resource(DoctorLogout, "/doctor/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(PatientRegister, '/patient/reg')
api.add_resource(Patient, '/patient/<int:patient_id>')
api.add_resource(PatientLogin, '/patient/login')
#api.add_resource(TokenRefresh, '/patient/refresh')
api.add_resource(PatientLogout, '/patient/logout')

if __name__ == "__main__":
    from db import db

    db.init_app(app)
    app.run(host="localhost", port=5000, debug=True)
