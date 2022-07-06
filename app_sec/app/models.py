import datetime
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=30, default='default@mail.com')
    admin = models.BooleanField(default=False)


def img_validator(img_url):
    print('validating')
    img_hosts = ['https://imgur.com/', 'https://imgbb.com/', 'https://i.ibb.co/', 'https://i.imgur.com/']
    for img_host in img_hosts:
        if img_url.startswith(img_host):
            print('valid')
            return True
    print('invalid')
    raise ValidationError('Invalid image URL.')


class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    img_url = models.URLField(validators=[img_validator])
    title = models.CharField(max_length=500)
    content = models.CharField(max_length=10000)
    date = models.DateTimeField()
    hidden = models.BooleanField(default=False)

    @property
    def date_pretty(self):
        return datetime.now().strftime("%c")


class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(default=datetime.now(), null=False)
    hidden = models.BooleanField(default=False)

    @property
    def date_pretty(self):
        return None if self.date is None else self.date.strftime("%c")
