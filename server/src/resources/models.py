from django.conf import settings
from django.db import models


class Resource(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<%s: title=%s, owner=%s>" % (
            self.__class__.__name__,
            self.title,
            self.owner,
        )


class Quota(models.Model):
    amount = models.PositiveSmallIntegerField(default=0)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.amount)

    def __repr__(self):
        return "<%s: amount=%s, user=%s>" % (
            self.__class__.__name__,
            str(self.amount),
            self.user,
        )
