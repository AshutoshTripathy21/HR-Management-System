from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta, time

class HRAccount(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Use hashed passwords in practice

    def __str__(self):
        return self.email


class Employee(models.Model):
    employee_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    dob = models.DateField()
    leaves = models.IntegerField(default=0)
    otp = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"
    

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    time = models.TimeField(default=timezone.now)

    class Meta:
        unique_together = ('employee', 'date')

class AttendanceHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    request_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.employee.name} - {self.status}"


class Logoff(models.Model):
    attendance = models.OneToOneField(Attendance, on_delete=models.CASCADE)
    logoff_time = models.DateTimeField(default=timezone.now)

    @property
    def work_hours(self):
        logoff_datetime = self.logoff_time

        # Combine the date and time to create a datetime object and make it timezone-aware
        present_datetime = datetime.combine(
            self.attendance.date,
            self.attendance.time if isinstance(self.attendance.time, time) else self.attendance.time.time()
        )

        # Make present_datetime timezone-aware
        present_datetime = timezone.make_aware(present_datetime, timezone.get_current_timezone())

        # Calculate the duration
        duration = logoff_datetime - present_datetime
        return round(duration.total_seconds() / 3600, 2)  # Convert to hours and round to 2 decimal places

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.employee.name} uploaded on {self.uploaded_at}"
    

class Group(models.Model):
    task_name = models.CharField(max_length=100)
    task_details = models.TextField()
    deadline = models.DateField()
    leader_name = models.CharField(max_length=100)
    leader_id = models.CharField(max_length=100)
    members = models.ManyToManyField(Employee, related_name='groups')

    def __str__(self):
        return self.task_name