from django.db import models

# Create your models here.

class MemoryLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    size_kb = models.IntegerField()
    count = models.IntegerField()