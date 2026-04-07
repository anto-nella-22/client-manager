from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("company", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planning", "Planning"),
                            ("active", "Active"),
                            ("on_hold", "On hold"),
                            ("completed", "Completed"),
                        ],
                        default="planning",
                        max_length=20,
                    ),
                ),
                ("deadline", models.DateField()),
                ("budget", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to="core.client",
                    ),
                ),
            ],
            options={"ordering": ["deadline", "title"]},
        ),
        migrations.CreateModel(
            name="TimeEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hours", models.DecimalField(decimal_places=2, max_digits=6)),
                ("date", models.DateField()),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_entries",
                        to="core.project",
                    ),
                ),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=50, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("sent", "Sent"),
                            ("paid", "Paid"),
                            ("overdue", "Overdue"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("pdf_file", models.FileField(blank=True, upload_to="invoices/pdfs/")),
                ("sent_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoices",
                        to="core.project",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
