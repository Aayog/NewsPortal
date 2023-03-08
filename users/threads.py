import threading

# from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        email = EmailMessage(self.subject, self.message, to=self.recipient_list)
        email.content_subtype = "html"
        print(email)
        email.send(fail_silently=False)


def send_email(subject, message, recipient_list):
    EmailThread(subject, message, recipient_list).start()
