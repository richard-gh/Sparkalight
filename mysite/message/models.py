from django.db import models
from pet.models import Person

class Thread(models.Model):
    subject = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(Person, on_delete=models.CASCADE)


class Message(models.Model):
    user = models.ForeignKey(Person, related_name='sender', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Person, related_name='recipient', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    body = models.CharField(max_length=1000)
    read = models.BooleanField(default=False)
    sentmessage = models.BooleanField(default=False)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    draft = models.BooleanField(default=False)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_recipient = models.BooleanField(default=False)
  
    def __unicode__(self):
        return self.body

