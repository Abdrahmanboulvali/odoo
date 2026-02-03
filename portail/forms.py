from django import forms


class DemandeCongeForm(forms.Form):
    employee_id = forms.ChoiceField(
        label="Employé",
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    leave_type_id = forms.ChoiceField(
        label="Type de congé",
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    date_from = forms.DateField(
        label="Date début",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    date_to = forms.DateField(
        label="Date fin",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    reason = forms.CharField(
        label="Motif",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Motif (optionnel)"})
    )


class AllocationForm(forms.Form):
    employee_id = forms.ChoiceField(
        label="Employé",
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    leave_type_id = forms.ChoiceField(
        label="Type de congé",
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    number_of_days = forms.FloatField(
        label="Nombre de jours",
        min_value=0.0,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.5"})
    )

    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Attribution via Portail RH"})
    )
