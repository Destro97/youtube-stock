from django.db import models

class Video(models.Model):
    video_id = models.CharField(max_length=40)
    title = models.CharField(max_length=255)
    description = models.TextField()
    published_at = models.DateTimeField()
    publisher = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'video'
        db_table = 'video'
        indexes = [
            models.Index(fields=['title', 'description']),
        ]
