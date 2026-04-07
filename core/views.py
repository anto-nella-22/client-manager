import json
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, RedirectView, TemplateView
from weasyprint import HTML

from .models import Client, Invoice, Project


class AuthLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class HomeRedirectView(RedirectView):
    pattern_name = "dashboard"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paid_invoices = Invoice.objects.filter(status=Invoice.Status.PAID)
        monthly_revenue = (
            paid_invoices.annotate(month=ExtractMonth("sent_date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        month_lookup = {item["month"]: float(item["total"] or 0) for item in monthly_revenue if item["month"]}
        labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        revenue_data = [month_lookup.get(index, 0) for index in range(1, 13)]
        total_revenue = paid_invoices.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        context.update(
            {
                "client_count": Client.objects.count(),
                "project_count": Project.objects.count(),
                "invoice_count": Invoice.objects.count(),
                "time_entry_hours": Project.objects.aggregate(total=Sum("time_entries__hours"))["total"] or Decimal("0.00"),
                "total_revenue": total_revenue,
                "recent_invoices": Invoice.objects.select_related("project", "project__client")[:5],
                "chart_labels": json.dumps(labels),
                "chart_data": json.dumps(revenue_data),
            }
        )
        return context


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "core/client_list.html"
    context_object_name = "clients"


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "core/project_list.html"
    context_object_name = "projects"
    queryset = Project.objects.select_related("client")


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "core/invoice_list.html"
    context_object_name = "invoices"
    queryset = Invoice.objects.select_related("project", "project__client")


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "core/invoice_detail.html"
    context_object_name = "invoice"
    queryset = Invoice.objects.select_related("project", "project__client")


def build_invoice_pdf(invoice, request):
    html_string = render_to_string(
        "core/pdf/invoice_pdf.html",
        {
            "invoice": invoice,
            "generated_on": timezone.now(),
            "site_name": "Client Manager",
        },
    )
    base_url = request.build_absolute_uri("/")
    pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()
    return pdf_bytes


@login_required
def invoice_pdf_view(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("project", "project__client"), pk=pk)
    pdf_bytes = build_invoice_pdf(invoice, request)
    filename = f"{invoice.number}.pdf"
    invoice.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response


@require_POST
@login_required
def email_invoice_view(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("project", "project__client"), pk=pk)
    pdf_bytes = build_invoice_pdf(invoice, request)
    filename = f"{invoice.number}.pdf"
    email = EmailMessage(
        subject=f"Invoice {invoice.number}",
        body=render_to_string(
            "core/email/invoice_email.txt",
            {
                "invoice": invoice,
            },
        ),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "billing@example.com"),
        to=[invoice.project.client.email],
    )
    email.attach(filename, pdf_bytes, "application/pdf")
    email.send(fail_silently=False)

    invoice.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
    invoice.sent_date = date.today()
    if invoice.status == Invoice.Status.DRAFT:
        invoice.status = Invoice.Status.SENT
    invoice.save(update_fields=["pdf_file", "sent_date", "status"])

    messages.success(request, f"Invoice {invoice.number} emailed to {invoice.project.client.email}.")
    return redirect(invoice.get_absolute_url())
