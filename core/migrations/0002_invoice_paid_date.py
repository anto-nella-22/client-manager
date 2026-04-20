from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="paid_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
