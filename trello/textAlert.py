import smtplib

def sendEmail(fromAddress, pswd, to, subject, body):
    gmail_user = fromAddress
    gmail_password = pswd

    to = to 
    subject = subject
    body = body

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (fromAddress, ", ".join(to), subject, body)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(fromAddress, to, email_text)
    server.close()

