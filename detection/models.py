from django.db import models
from django.contrib.auth.models import User


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    condition = models.CharField(max_length=100)

    date = models.DateField()
    time = models.TimeField()

    # ✅ ADD THIS (IMPORTANT)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_doctor = models.BooleanField(default=True)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"

class DetectionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
    result = models.CharField(max_length=100)
    confidence = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        ordering = ['-date'] 
    def __str__(self):
        return self.user.username