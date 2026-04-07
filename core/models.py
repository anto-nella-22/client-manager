from decimal import Decimal

from django.db import models
from django.urls import reverse


class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.company})"


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On hold"
        COMPLETED = "completed", "Completed"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    deadline = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["deadline", "title"]

    def __str__(self):
        return self.title


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="invoices")
    number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    pdf_file = models.FileField(upload_to="invoices/pdfs/", blank=True)
    sent_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    def get_absolute_url(self):
        return reverse("invoice_detail", args=[self.pk])


class TimeEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="time_entries")
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.project.title} - {self.hours}h"

