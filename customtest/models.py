from django.db import models

# Create your models here.

class MemoryLog(models.Model):
    memorylog_id = models.AutoField(primary_key=True, verbose_name='Id')
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    size_kb = models.IntegerField()
    count = models.IntegerField()