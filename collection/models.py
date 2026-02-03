import uuid
from django.db import models

class Consumer(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    ssn = models.CharField(max_length=11, unique=True, db_index=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    STATUS_CHOICES = [
        ('INACTIVE', 'Inactive'),
        ('IN_COLLECTION', 'In Collection'),
        ('PAID_IN_FULL', 'Paid In Full'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_reference = models.CharField(max_length=255, db_index=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    consumers = models.ManyToManyField(Consumer, related_name='accounts')

    def __str__(self):
        return self.client_reference
