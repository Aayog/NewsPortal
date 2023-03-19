import threading
from django.core.mail import EmailMessage


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list, content_subtype="html"):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.content_subtype = content_subtype
        threading.Thread.__init__(self)

    def run(self):
        email = EmailMessage(self.subject, self.message, to=self.recipient_list)
        email.content_subtype = self.content_subtype
        email.send(fail_silently=False)


def send_email(subject, message, recipient_list, content_subtype="html"):
    EmailThread(subject, message, recipient_list, content_subtype).start()
