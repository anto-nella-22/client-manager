from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Client, Invoice, Project, TimeEntry


class Command(BaseCommand):
    help = "Create a demo superuser and sample CRM data."

    def handle(self, *args, **options):
        user_model = get_user_model()
        username = "admin"
        email = "admin@example.com"
        password = "admin12345"

        if not user_model.objects.filter(username=username).exists():
            user_model.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created superuser {username}/{password}"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists."))

        acme, _ = Client.objects.get_or_create(
            email="sarah@acme.test",
            defaults={
                "name": "Sarah Connor",
                "company": "Acme Studio",
                "phone": "+1 555 0100",
            },
        )
        globex, _ = Client.objects.get_or_create(
            email="leo@globex.test",
            defaults={
                "name": "Leo Barnes",
                "company": "Globex Corp",
                "phone": "+1 555 0101",
            },
        )

        website, _ = Project.objects.get_or_create(
            client=acme,
            title="Website Redesign",
            defaults={
                "status": Project.Status.ACTIVE,
                "deadline": date.today() + timedelta(days=21),
                "budget": Decimal("8500.00"),
            },
        )
        retainer, _ = Project.objects.get_or_create(
            client=globex,
            title="Growth Retainer",
            defaults={
                "status": Project.Status.ON_HOLD,
                "deadline": date.today() + timedelta(days=45),
                "budget": Decimal("12000.00"),
            },
        )

        Invoice.objects.get_or_create(
            project=website,
            number="INV-1001",
            defaults={
                "amount": Decimal("3200.00"),
                "status": Invoice.Status.PAID,
                "sent_date": date.today() - timedelta(days=20),
            },
        )
        Invoice.objects.get_or_create(
            project=website,
            number="INV-1002",
            defaults={
                "amount": Decimal("1800.00"),
                "status": Invoice.Status.SENT,
                "sent_date": date.today() - timedelta(days=4),
            },
        )
        Invoice.objects.get_or_create(
            project=retainer,
            number="INV-1003",
            defaults={
                "amount": Decimal("2500.00"),
                "status": Invoice.Status.DRAFT,
            },
        )

        TimeEntry.objects.get_or_create(
            project=website,
            date=date.today() - timedelta(days=2),
            description="Homepage UX refinements",
            defaults={"hours": Decimal("4.50")},
        )
        TimeEntry.objects.get_or_create(
            project=website,
            date=date.today() - timedelta(days=1),
            description="Component implementation",
            defaults={"hours": Decimal("6.00")},
        )
        TimeEntry.objects.get_or_create(
            project=retainer,
            date=date.today() - timedelta(days=5),
            description="Monthly analytics review",
            defaults={"hours": Decimal("2.50")},
        )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))

