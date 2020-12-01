from flask import current_app as app, g
from flask_mail import Mail, Message

def get_mail_instance():
    if not hasattr(g, 'mail'):
        g.mail = Mail(app)
        g.mail.init_app(app)

    return g.mail


def send_verification_email(email, user_id, token):
    url = app.config["VERIFICATION_URL"]
    subject = "Verify SecureTrade Account"
    text_body = "Click here to verify your SecureTrade account: %s?id=%s&token=%s\nThis link is valid for 30 minutes." % (url, user_id, token)

    msg = Message(subject, sender=app.config["MAIL_USERNAME"])
    msg.body = text_body
    msg.recipients = [email]

    get_mail_instance().send(msg)
    