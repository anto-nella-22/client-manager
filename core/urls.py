from django.urls import path

from . import views


urlpatterns = [
    path("", views.HomeRedirectView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf_view, name="invoice_pdf"),
    path("invoices/<int:pk>/email/", views.email_invoice_view, name="invoice_email"),
]

