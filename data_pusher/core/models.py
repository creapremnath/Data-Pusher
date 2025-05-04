from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

#User db model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# Role Db model
class Role(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]
    role_name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name

    class Meta:
        # Ensure the role_name is unique, which it is, but explicitly stating that
        constraints = [
            models.UniqueConstraint(fields=['role_name'], name='unique_role_name')
        ]

#Account/Organisation db model
class Account(models.Model):
    account_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    account_name = models.CharField(max_length=255)  # mandatory
    app_secret_token = models.CharField(default=uuid.uuid4, unique=True)  # automatically generated
    website = models.URLField(blank=True, null=True)  # Optional
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.account_name

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'


#Account/Org_member db model
class AccountMember(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='members')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account_memberships')
    role_id = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('account_id', 'user_id')  # Corrected field names

    def __str__(self):
        return f'{self.user_id.email} in {self.account_id.account_name} as {self.role_id.role_name if self.role_id else "No Role"}'


#Destination Db model
class Destination(models.Model):
    destination_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destinations')
    url = models.URLField()
    http_method = models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT')])
    headers = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.account_id.account_name} - {self.url}'

    class Meta:
        verbose_name = 'Destination'
        verbose_name_plural = 'Destinations'


class Log(models.Model):
    event_id = models.CharField(default=uuid.uuid4, max_length=255, unique=True)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='account_id')  # Specify column name
    destination_id = models.ForeignKey(Destination, on_delete=models.CASCADE, db_column='destination_id')  # Specify column name
    received_timestamp = models.DateTimeField()
    processed_timestamp = models.DateTimeField()
    received_data = models.JSONField()
    status = models.CharField(max_length=10, choices=[('success', 'Success'), ('failed', 'Failed')])

    def __str__(self):
        return f'Log for Event {self.event_id} - {self.status}'

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'


