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
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, RedirectView, TemplateView, UpdateView
from weasyprint import HTML

from .forms import ClientForm, InvoiceForm, ProjectForm, TimeEntryForm
from .models import Client, Invoice, Project, TimeEntry


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
            paid_invoices.annotate(month=ExtractMonth("paid_date"))
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["client_create_url"] = reverse_lazy("client_create")
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "core/form.html"
    success_url = reverse_lazy("client_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Clients", "url": reverse_lazy("client_list")},
                    {"label": "Add Client", "url": None},
                ],
                "page_eyebrow": "Client Setup",
                "page_title": "Add Client",
                "page_subtitle": "Create a client record with the key contact and company information your projects rely on.",
                "cancel_url": reverse_lazy("client_list"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Client {form.instance.name} created.")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "core/form.html"
    success_url = reverse_lazy("client_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Clients", "url": reverse_lazy("client_list")},
                    {"label": "Edit Client", "url": None},
                ],
                "page_eyebrow": "Client Setup",
                "page_title": "Edit Client",
                "page_subtitle": "Refine client details so future work, invoices, and communication stay accurate.",
                "cancel_url": reverse_lazy("client_list"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Client {form.instance.name} updated.")
        return super().form_valid(form)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "core/project_list.html"
    context_object_name = "projects"
    queryset = Project.objects.select_related("client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "project_create_url": reverse_lazy("project_create"),
                "client_create_url": reverse_lazy("client_create"),
            }
        )
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "core/form.html"
    success_url = reverse_lazy("project_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Projects", "url": reverse_lazy("project_list")},
                    {"label": "Add Project", "url": None},
                ],
                "page_eyebrow": "Project Setup",
                "page_title": "Add Project",
                "page_subtitle": "Define the scope, budget, deadline, and current status of a client engagement.",
                "cancel_url": reverse_lazy("project_list"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Project {form.instance.title} created.")
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "core/form.html"
    success_url = reverse_lazy("project_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Projects", "url": reverse_lazy("project_list")},
                    {"label": "Edit Project", "url": None},
                ],
                "page_eyebrow": "Project Setup",
                "page_title": "Edit Project",
                "page_subtitle": "Keep the project schedule, budget, and delivery status aligned with real client work.",
                "cancel_url": reverse_lazy("project_list"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Project {form.instance.title} updated.")
        return super().form_valid(form)


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "core/invoice_list.html"
    context_object_name = "invoices"
    queryset = Invoice.objects.select_related("project", "project__client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "invoice_create_url": reverse_lazy("invoice_create"),
                "project_create_url": reverse_lazy("project_create"),
            }
        )
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "core/form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Invoices", "url": reverse_lazy("invoice_list")},
                    {"label": "Create Invoice", "url": None},
                ],
                "page_eyebrow": "Billing Setup",
                "page_title": "Create Invoice",
                "page_subtitle": "Prepare a bill with status and dates that can move cleanly through the payment workflow.",
                "cancel_url": reverse_lazy("invoice_list"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Invoice {form.instance.number} created.")
        return super().form_valid(form)


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "core/form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Invoices", "url": reverse_lazy("invoice_list")},
                    {"label": "Edit Invoice", "url": None},
                ],
                "page_eyebrow": "Billing Setup",
                "page_title": "Edit Invoice",
                "page_subtitle": "Update billing details without leaving the client-facing workflow.",
                "cancel_url": self.object.get_absolute_url(),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, f"Invoice {form.instance.number} updated.")
        return super().form_valid(form)


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "core/invoice_detail.html"
    context_object_name = "invoice"
    queryset = Invoice.objects.select_related("project", "project__client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = context["invoice"]
        actions = []

        if invoice.status != Invoice.Status.SENT:
            actions.append(
                {
                    "label": "Mark as Sent",
                    "status": Invoice.Status.SENT,
                    "style": "secondary",
                }
            )
        if invoice.status != Invoice.Status.PAID:
            actions.append(
                {
                    "label": "Mark as Paid",
                    "status": Invoice.Status.PAID,
                    "style": "primary",
                }
            )
        if invoice.status != Invoice.Status.OVERDUE:
            actions.append(
                {
                    "label": "Mark as Overdue",
                    "status": Invoice.Status.OVERDUE,
                    "style": "tertiary",
                }
            )

        context["status_actions"] = actions
        context["invoice_breadcrumbs"] = [
            {"label": "Dashboard", "url": reverse_lazy("dashboard")},
            {"label": "Invoices", "url": reverse_lazy("invoice_list")},
            {"label": invoice.number, "url": None},
        ]
        return context


class TimeEntryCreateView(LoginRequiredMixin, CreateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = "core/form.html"
    success_url = reverse_lazy("dashboard")

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get("project")
        if project_id:
            initial["project"] = project_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Log Time", "url": None},
                ],
                "page_eyebrow": "Time Tracking",
                "page_title": "Log Time",
                "page_subtitle": "Capture work delivered so budgets, profitability, and client reporting stay grounded in reality.",
                "cancel_url": reverse_lazy("dashboard"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Time entry created.")
        return super().form_valid(form)


class TimeEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = "core/form.html"
    success_url = reverse_lazy("dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_breadcrumbs": [
                    {"label": "Dashboard", "url": reverse_lazy("dashboard")},
                    {"label": "Edit Time Entry", "url": None},
                ],
                "page_eyebrow": "Time Tracking",
                "page_title": "Edit Time Entry",
                "page_subtitle": "Adjust logged work when the project record needs cleaner detail or corrected hours.",
                "cancel_url": reverse_lazy("dashboard"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Time entry updated.")
        return super().form_valid(form)


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


@require_POST
@login_required
def invoice_status_update_view(request, pk, status):
    invoice = get_object_or_404(Invoice.objects.select_related("project", "project__client"), pk=pk)
    today = date.today()
    valid_statuses = {choice for choice, _label in Invoice.Status.choices}

    if status not in valid_statuses:
        messages.error(request, "That invoice status is not supported.")
        return redirect(invoice.get_absolute_url())

    invoice.status = status

    if status == Invoice.Status.SENT:
        invoice.sent_date = invoice.sent_date or today
        invoice.paid_date = None
    elif status == Invoice.Status.PAID:
        invoice.sent_date = invoice.sent_date or today
        invoice.paid_date = today
    else:
        invoice.paid_date = None

    invoice.save(update_fields=["status", "sent_date", "paid_date"])
    messages.success(request, f"Invoice {invoice.number} marked as {invoice.get_status_display().lower()}.")
    return redirect(invoice.get_absolute_url())
