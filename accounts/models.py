from django.db import models


class Question(models.Model):
    image = models.ImageField(upload_to='photos')
    answer = models.CharField(max_length=255)

    def delete(self, *args, **kwargs):
        self.image.delete(False)
        super(Question, self).delete(*args, **kwargs)
