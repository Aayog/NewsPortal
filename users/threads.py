import threading

# from django.core.mail import send_mail
from django.conf import settings


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        email = EmailMessage(self.subject, self.message, to=self.recipient_list)
        email.content_subtype = "html"
        print(email)
        email.send(fail_silently=False)


def send_email(email):
    EmailThread(email).start()
