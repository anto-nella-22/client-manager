from django import forms

from .models import Client, Invoice, Project, TimeEntry


class SearchForm(forms.Form):
    query = forms.CharField(required=False)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                continue
            if isinstance(widget, (forms.SelectDateWidget,)):
                continue

            css_class = "app-select" if isinstance(widget, forms.Select) else "app-input"
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {css_class}".strip()


class ClientForm(StyledModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "company", "phone"]


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = ["client", "title", "status", "deadline", "budget"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }


class InvoiceForm(StyledModelForm):
    class Meta:
        model = Invoice
        fields = ["project", "number", "amount", "status", "sent_date", "paid_date", "pdf_file"]
        widgets = {
            "sent_date": forms.DateInput(attrs={"type": "date"}),
            "paid_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        sent_date = cleaned_data.get("sent_date")
        paid_date = cleaned_data.get("paid_date")

        if status == Invoice.Status.PAID and not paid_date:
            self.add_error("paid_date", "Paid invoices should include a payment date.")

        if status == Invoice.Status.PAID and not sent_date:
            self.add_error("sent_date", "Paid invoices should include the date they were sent.")

        if status != Invoice.Status.PAID:
            cleaned_data["paid_date"] = None

        return cleaned_data


class TimeEntryForm(StyledModelForm):
    class Meta:
        model = TimeEntry
        fields = ["project", "hours", "date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }
