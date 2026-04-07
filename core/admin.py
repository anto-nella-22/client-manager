from django.contrib import admin

from .models import Client, Invoice, Project, TimeEntry


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "phone")
    search_fields = ("name", "company", "email", "phone")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "status", "deadline", "budget")
    list_filter = ("status", "deadline")
    search_fields = ("title", "client__name", "client__company")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "project", "status", "amount", "sent_date")
    list_filter = ("status", "sent_date")
    search_fields = ("number", "project__title", "project__client__name")


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ("project", "date", "hours", "description")
    list_filter = ("date",)
    search_fields = ("project__title", "description")

