from django.db import models

class OperationRoom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    
class Surgeon(models.Model):
    DAYS_OF_WEEK = [
        ('Pazartesi', 'Pazartesi'),
        ('Salı','Salı'),
        ('Çarşamba','Çarşamba'),
        ('Perşembe','Perşembe')
        ('Cuma','Cuma')    
    ]
    name=models.CharField(max_length=50)
    specialty = models.CharField(max_length=100)
    off_day = models.CharField(max_length=20,choices=DAYS_OF_WEEK, blank=True, null=True)

    
