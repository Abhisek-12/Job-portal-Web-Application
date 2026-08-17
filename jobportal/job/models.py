from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    EMPLOYER = 'employer'
    CANDIDATE = 'candidate'
    ROLE_CHOICES = [
        (EMPLOYER, 'Employer'),
        (CANDIDATE, 'Candidate'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Job(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'applicant'], name='unique_job_application')
        ]

    def __str__(self):
        return self.applicant.username


class SavedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.candidate.username} saved {self.job.title}"
