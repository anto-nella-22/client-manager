from django.urls import path

from . import views


urlpatterns = [
    path("", views.HomeRedirectView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/new/", views.ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client_update"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/new/", views.ProjectCreateView.as_view(), name="project_create"),
    path("projects/<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="project_update"),
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/new/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoices/<int:pk>/edit/", views.InvoiceUpdateView.as_view(), name="invoice_update"),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf_view, name="invoice_pdf"),
    path("invoices/<int:pk>/email/", views.email_invoice_view, name="invoice_email"),
    path("invoices/<int:pk>/status/<str:status>/", views.invoice_status_update_view, name="invoice_status_update"),
    path("time-entries/new/", views.TimeEntryCreateView.as_view(), name="timeentry_create"),
    path("time-entries/<int:pk>/edit/", views.TimeEntryUpdateView.as_view(), name="timeentry_update"),
]
