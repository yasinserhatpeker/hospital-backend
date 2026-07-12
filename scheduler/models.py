from django.db import models

class OperationRoom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} - {self.room_type}"
    
    
class Surgeon(models.Model):
    DAYS_OF_WEEK = [
        ('Pazartesi', 'Pazartesi'),
        ('Salı','Salı'),
        ('Çarşamba','Çarşamba'),
        ('Perşembe','Perşembe'),
        ('Cuma','Cuma'), 
    ]
    name=models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    off_day = models.CharField(max_length=20,choices=DAYS_OF_WEEK, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.specialty}"
    
    

class Surgery(models.Model):
    PRIORITY_CHOICES = [
        ('Düşük', 'Düşük'),
        ('Orta','Orta'),
        ('Yüksek','Yüksek'),
        ('Kritik','Kritik'),
    ]
    patient_name = models.CharField(max_length=100)
    surgeon = models.ForeignKey(Surgeon, on_delete=models.CASCADE, null=True, blank=True)
    operation_name = models.CharField(max_length=100)
    required_specialty = models.CharField(max_length=200)
    duration_slots = models.IntegerField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    required_room = models.ForeignKey(OperationRoom, on_delete=models.SET_NULL, null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.patient_name} - {self.required_specialty}"


class Constraints(models.Model):
    RULE_TYPES=[
        ('HARD', 'Hard Constraint (Kesin)'),
        ('SOFT', 'Soft Constraint(Esnek)'),
    ]

    CONSTRAINT_KEYS = [
        ('priority_weight', 'Öncelik Ağırlığı (Sıralama)'),
        ('duration_weight', 'Süre Ağırlığı (Sıralama)'),
        ('surgeon_off_day', 'Cerrah İzin Günü'),
        ('max_daily_surgeries', 'Cerrah Başı Günlük Maksimum Ameliyat'),
        ('min_rest_slots', 'Ameliyatlar Arası Minimum Dinlenme (Slot)'),
    ]

    name = models.CharField(max_length=100, choices=CONSTRAINT_KEYS, unique=True)
    description = models.TextField()
    rule_type = models.CharField(max_length=10 , choices=RULE_TYPES)
    is_active = models.BooleanField(default=True)
    value = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.name} - {self.rule_type}"



class AnesthesiaTeam(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name



class Schedule(models.Model):
    date = models.DateField()
    room = models.ForeignKey(OperationRoom, on_delete=models.CASCADE)
    surgeon = models.ForeignKey(Surgeon, on_delete=models.CASCADE)
    team = models.ForeignKey(AnesthesiaTeam, on_delete=models.CASCADE)
    surgery = models.ForeignKey(Surgery, on_delete=models.CASCADE)
    start_slot = models.IntegerField()
    end_slot = models.IntegerField()
    
    
    def __str__(self):
        return f"{self.room.name} | Slot = {self.start_slot} - {self.end_slot} | {self.surgery.patient_name}"
    
