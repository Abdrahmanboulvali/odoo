from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from xmlrpc.client import Fault
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .odoo_client import (
    get_employees,
    get_employee_by_id,
    get_leaves,
    get_leave_types,
    create_leave,
    approve_leave,
    refuse_leave,
    create_allocation,
    get_allocations,
    approve_allocation,
    refuse_allocation,
)

from .forms import DemandeCongeForm, AllocationForm

# ==========================
# AUTH
# ==========================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")


    return render(request, "portail/registration/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ==========================
# LISTE EMPLOYES
# ==========================
@login_required
def liste_employes(request):
    q = request.GET.get("q", "").strip().lower()
    employes = get_employees()

    if q:
        employes = [e for e in employes if q in (e.get("name") or "").lower()]

    return render(request, "portail/liste_employes.html", {"employes": employes})


# ==========================
# FICHE EMPLOYE
# ==========================
@login_required
def fiche_employe(request, emp_id):
    employe = get_employee_by_id(emp_id)
    return render(request, "portail/fiche_employe.html", {"employe": employe})


# ==========================
# LISTE CONGES
# ==========================
@login_required
def liste_conges(request):
    leaves = get_leaves()
    return render(request, "portail/liste_conges.html", {"leaves": leaves})


# ==========================
# DEMANDER CONGE ✅ (Dropdown + gestion allocation)
# ==========================
@login_required
@require_http_methods(["GET", "POST"])
def demander_conge(request):
    employes = get_employees()
    types = get_leave_types()

    emp_choices = [(str(e["id"]), e["name"]) for e in employes]
    type_choices = [(str(t["id"]), t["name"]) for t in types]

    if request.method == "POST":
        form = DemandeCongeForm(request.POST)


        form.fields["employee_id"].choices = emp_choices
        form.fields["leave_type_id"].choices = type_choices

        if form.is_valid():
            employee_id = int(form.cleaned_data["employee_id"])
            leave_type_id = int(form.cleaned_data["leave_type_id"])
            date_from = form.cleaned_data["date_from"].isoformat()
            date_to = form.cleaned_data["date_to"].isoformat()
            reason = form.cleaned_data["reason"] or ""

            try:
                leave_id = create_leave(employee_id, leave_type_id, date_from, date_to, reason)
                messages.success(request, f"Demande envoyée ✅ (ID: {leave_id})")
                return redirect("liste_conges")

            except Fault as e:
                
                if "aucune attribution" in str(e).lower():
                    messages.error(
                        request,
                        "Vous n’avez aucune attribution pour ce type de congé. "
                        "Veuillez créer une attribution (Allocation) avant de soumettre la demande."
                    )
                    
                    return redirect(f"/allocations/nouvelle/?employee_id={employee_id}&leave_type_id={leave_type_id}")
                else:
                    messages.error(request, f"Erreur Odoo: {e}")

    else:
        form = DemandeCongeForm()
        
        form.fields["employee_id"].choices = emp_choices
        form.fields["leave_type_id"].choices = type_choices

    return render(request, "portail/demander_conge.html", {"form": form})


# ==========================
# APPROUVER CONGE
# ==========================
@login_required
@require_http_methods(["POST"])
def approuver_conge(request, leave_id):
    approve_leave(leave_id)
    messages.success(request, "Congé approuvé ✅")
    return redirect("liste_conges")


# ==========================
# REFUSER CONGE
# ==========================
@login_required
@require_http_methods(["POST"])
def refuser_conge(request, leave_id):
    refuse_leave(leave_id)
    messages.warning(request, "Congé refusé")
    return redirect("liste_conges")


# ==========================
# LISTE ALLOCATIONS
# ==========================
@login_required
def liste_allocations(request):
    allocations = get_allocations()
    return render(request, "portail/liste_allocations.html", {"allocations": allocations})


# ==========================
# CREER ALLOCATION ✅ (Dropdown + Prefill par GET params)
# ==========================
@login_required
@require_http_methods(["GET", "POST"])
def creer_allocation(request):
    employes = get_employees()
    types = get_leave_types()

    emp_choices = [(str(e["id"]), e["name"]) for e in employes]
    type_choices = [(str(t["id"]), t["name"]) for t in types]


    initial_data = {}
    if request.method == "GET":
        if request.GET.get("employee_id"):
            initial_data["employee_id"] = str(request.GET.get("employee_id"))
        if request.GET.get("leave_type_id"):
            initial_data["leave_type_id"] = str(request.GET.get("leave_type_id"))

    if request.method == "POST":
        form = AllocationForm(request.POST)


        form.fields["employee_id"].choices = emp_choices
        form.fields["leave_type_id"].choices = type_choices

        if form.is_valid():
            employee_id = int(form.cleaned_data["employee_id"])
            leave_type_id = int(form.cleaned_data["leave_type_id"])
            number_of_days = float(form.cleaned_data["number_of_days"])
            description = form.cleaned_data.get("description") or "Attribution via Portail RH"

            try:
                allocation_id = create_allocation(employee_id, leave_type_id, number_of_days, description)
                messages.success(request, f"Attribution créée (ID: {allocation_id})")
                return redirect("liste_allocations")
            except Fault as e:
                messages.error(request, f"Erreur Odoo: {e}")

    else:
        form = AllocationForm(initial=initial_data)
        
        form.fields["employee_id"].choices = emp_choices
        form.fields["leave_type_id"].choices = type_choices

    return render(request, "portail/creer_allocation.html", {"form": form})


# ==========================
# APPROUVER ALLOCATION
# ==========================
@login_required
@require_http_methods(["POST"])
def approuver_allocation(request, allocation_id):
    approve_allocation(allocation_id)
    messages.success(request, "Allocation validée ✅")
    return redirect("liste_allocations")


# ==========================
# REFUSER ALLOCATION
# ==========================
@login_required
@require_http_methods(["POST"])
def refuser_allocation(request, allocation_id):
    refuse_allocation(allocation_id)
    messages.warning(request, "Allocation refusée ⚠️")
    return redirect("liste_allocations")

@login_required
def dashboard(request):
    employes = get_employees()
    leaves = get_leaves()
    allocations = get_allocations()

    total_employes = len(employes)

    conges_en_attente = [l for l in leaves if l.get("state") in ["confirm", "validate1"]]
    conges_approuves = [l for l in leaves if l.get("state") in ["validate", "validated"]]

    allocs_en_attente = [a for a in allocations if a.get("state") in ["draft", "confirm"]]

    # derniers enregistrements
    derniers_conges = sorted(leaves, key=lambda x: x.get("id", 0), reverse=True)[:5]
    dernieres_allocs = sorted(allocations, key=lambda x: x.get("id", 0), reverse=True)[:5]

    return render(request, "portail/dashboard.html", {
        "total_employes": total_employes,
        "conges_en_attente": len(conges_en_attente),
        "conges_approuves": len(conges_approuves),
        "allocs_en_attente": len(allocs_en_attente),
        "derniers_conges": derniers_conges,
        "dernieres_allocs": dernieres_allocs,
    })
