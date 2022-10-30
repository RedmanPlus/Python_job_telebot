from django.db import models
from manage import init_django

init_django()

class User(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True, null=False, blank=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(blank=True, null=True, max_length=255)
    language_code = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id}: {self.first_name} {self.last_name if self.last_name else ''}"
    
    @classmethod
    def get_summary(cls):
        return cls.objects.all().count()
