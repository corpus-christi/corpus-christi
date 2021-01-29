import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import request
from flask.json import jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from bs4 import BeautifulSoup


from . import emails
from .models import EmailSchema, Email, Recipient
from .. import db


# ---- Email

@emails.route('/', methods=['POST'])
@jwt_required
def send_email():
    # this route is intended to fail without proper credentials
    email_schema = EmailSchema()
    try:
        valid_email_request = email_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # username and password for a Gmail account
    EMAIL_ADDRESS = "corpus.christi.test@gmail.com"
    EMAIL_PASSWORD = "cc-email-test-password"

    SENDER_NAME = valid_email_request['managerName']
    SENDER_EMAIL = valid_email_request['managerEmail']
    # PATH_TO_CSV = sys.argv[3]
    SUBJECT = valid_email_request['subject']
    BODY = valid_email_request['body']
    recipients = valid_email_request['recipients']
    recipientIds = valid_email_request['recipientIds']
    senderId = valid_email_request['senderId']
    ATTACHMENT_PATH = False

    print(SENDER_EMAIL)
    print(SENDER_NAME)
    print(SUBJECT)
    print(BODY)
    print(recipients)

    newBody = BeautifulSoup(BODY, "html.parser")

    

    # grabbing the emails from the csv file and putting them into a list
    # recipients = []
    # with open(PATH_TO_CSV, 'r') as c:
    #    reader = csv.reader(c)
    #    for row in reader:
    #        recipients.append([row[0]])

    # this forms and sends the email
    def send(to_addr: str, subject: str, body: str, attachment: str = None):
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_NAME + ' <' + EMAIL_ADDRESS + '>'
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.add_header('reply-to', SENDER_EMAIL)
        msg.attach(MIMEText(newBody.get_text(), 'plain'))
        msg.attach(MIMEText(body, 'html'))
        if attachment:
            payload = create_attachement(attachment)
            msg.attach(payload)
        text = msg.as_string()
        print("text", text)
        smtp.sendmail(EMAIL_ADDRESS, recipients, text)

    # if an attachment is given, this function formats it to be sent
    def create_attachement(path: str):
        with open(path, 'rb') as f:
            content = f.read()
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(content)
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % f.name)
        return p

    # connect and login
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        send(EMAIL_ADDRESS, SUBJECT, BODY, ATTACHMENT_PATH)
    dbData = {'subject': SUBJECT, 'body': newBody.get_text(), 'sender_id':senderId}
    new_email= Email(**dbData)
    print("New email", new_email)
    db.session.add(new_email)
    db.session.commit()

    thisEmail = db.session.query(Email).filter_by(subject=SUBJECT).first() #Not guaranteed to find correct email if there are two with the same subject
    print("THIS EMAIL",thisEmail)
    for id in recipientIds:
        new_recipient=Recipient(**{'person_id':id, 'email_id':thisEmail.id})
        db.session.add(new_recipient)
        db.session.commit()

    return "Sent"
