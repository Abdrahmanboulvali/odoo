from django import forms


# =========================
# 1) Employé: Demander congé
# =========================


class DemandeCongeManagerForm(forms.Form):
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
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )



# =========================
# 2) Manager: Allocation
# =========================
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


# =========================
# 3) Manager: Créer employé + compte portail
# =========================
class CreateEmployeePortalForm(forms.Form):
    name = forms.CharField(
        label="Nom complet",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    work_email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    work_phone = forms.CharField(
        label="Téléphone",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    # ✅ Poste (lié à hr.job)
    job_id = forms.ChoiceField(
        label="Poste",
        required=False,
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"})
    )

class DemandeCongeEmployeeForm(forms.Form):
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
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )
