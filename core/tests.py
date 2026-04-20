import json
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Client, Invoice, Project, TimeEntry


class BaseAppTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester", password="pass12345")
        self.client.force_login(self.user)

        self.crm_client = Client.objects.create(
            name="Sarah Connor",
            email="sarah@example.com",
            company="Acme Studio",
            phone="+1 555 0100",
        )
        self.project = Project.objects.create(
            client=self.crm_client,
            title="Website Redesign",
            status=Project.Status.ACTIVE,
            deadline=date(2026, 5, 10),
            budget=Decimal("12500.00"),
        )


class InvoiceWorkflowTests(BaseAppTestCase):
    def test_mark_invoice_paid_sets_paid_date_and_sent_date(self):
        invoice = Invoice.objects.create(
            project=self.project,
            number="INV-2001",
            amount=Decimal("3200.00"),
            status=Invoice.Status.DRAFT,
        )

        response = self.client.post(reverse("invoice_status_update", args=[invoice.pk, Invoice.Status.PAID]))

        self.assertRedirects(response, reverse("invoice_detail", args=[invoice.pk]))
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.PAID)
        self.assertEqual(invoice.sent_date, date.today())
        self.assertEqual(invoice.paid_date, date.today())

    def test_mark_invoice_overdue_clears_paid_date(self):
        invoice = Invoice.objects.create(
            project=self.project,
            number="INV-2002",
            amount=Decimal("2100.00"),
            status=Invoice.Status.PAID,
            sent_date=date(2026, 4, 1),
            paid_date=date(2026, 4, 3),
        )

        self.client.post(reverse("invoice_status_update", args=[invoice.pk, Invoice.Status.OVERDUE]))

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.OVERDUE)
        self.assertIsNone(invoice.paid_date)
        self.assertEqual(invoice.sent_date, date(2026, 4, 1))

    def test_dashboard_revenue_uses_paid_date_month(self):
        Invoice.objects.create(
            project=self.project,
            number="INV-2003",
            amount=Decimal("1500.00"),
            status=Invoice.Status.PAID,
            sent_date=date(2026, 1, 20),
            paid_date=date(2026, 2, 4),
        )
        Invoice.objects.create(
            project=self.project,
            number="INV-2004",
            amount=Decimal("500.00"),
            status=Invoice.Status.SENT,
            sent_date=date(2026, 2, 8),
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        chart_data = json.loads(response.context["chart_data"])
        self.assertEqual(chart_data[1], 1500.0)
        self.assertEqual(chart_data[0], 0)


class FormFlowTests(BaseAppTestCase):
    def test_client_create_flow_works_in_app(self):
        response = self.client.post(
            reverse("client_create"),
            data={
                "name": "Leo Barnes",
                "email": "leo@example.com",
                "company": "Globex Corp",
                "phone": "+1 555 0101",
            },
        )

        self.assertRedirects(response, reverse("client_list"))
        self.assertTrue(Client.objects.filter(email="leo@example.com").exists())

    def test_invoice_create_validates_paid_date_when_status_is_paid(self):
        response = self.client.post(
            reverse("invoice_create"),
            data={
                "project": self.project.pk,
                "number": "INV-2005",
                "amount": "1800.00",
                "status": Invoice.Status.PAID,
                "sent_date": "2026-04-10",
                "paid_date": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("paid_date", form.errors)
        self.assertFalse(Invoice.objects.filter(number="INV-2005").exists())

    def test_time_entry_create_flow_works_in_app(self):
        response = self.client.post(
            reverse("timeentry_create"),
            data={
                "project": self.project.pk,
                "hours": "3.50",
                "date": "2026-04-19",
                "description": "Homepage polish",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(TimeEntry.objects.filter(description="Homepage polish").exists())


class TemplateRenderingTests(BaseAppTestCase):
    def test_invoice_list_empty_state_and_status_badge_render(self):
        Invoice.objects.create(
            project=self.project,
            number="INV-2006",
            amount=Decimal("2500.00"),
            status=Invoice.Status.OVERDUE,
        )

        response = self.client.get(reverse("invoice_list"))

        self.assertContains(response, "status-overdue")
        self.assertContains(response, "$2,500.00")
