from .decorators import employee_required
from .decorators import manager_required
from django.views.decorators.http import require_http_methods
from xmlrpc.client import Fault
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db import transaction
import re

from .models import Profile
from .odoo_client import create_employee, get_jobs
from .forms import DemandeCongeManagerForm, DemandeCongeEmployeeForm, AllocationForm, CreateEmployeePortalForm

from django.contrib.auth.decorators import user_passes_test


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



from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

# ==========================
# AUTH
# ==========================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


def is_manager(user):
    return user.is_authenticated and user.is_staff


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect("dashboard")
            return redirect("employee_home")

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
@manager_required
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
    types = get_leave_types()
    type_choices = [(str(t["id"]), t["name"]) for t in types]

    is_staff = request.user.is_staff

    FormClass = DemandeCongeManagerForm if is_staff else DemandeCongeEmployeeForm
    form = FormClass(request.POST or None)

    # choices type congé
    form.fields["leave_type_id"].choices = type_choices

    # ✅ فقط المدير يحتاج employee_id (الموظف لا يملك هذا الحقل)
    if is_staff and "employee_id" in form.fields:
        employes = get_employees()
        form.fields["employee_id"].choices = [(str(e["id"]), e["name"]) for e in employes]

    if request.method == "POST" and form.is_valid():
        leave_type_id = int(form.cleaned_data["leave_type_id"])
        date_from = form.cleaned_data["date_from"].isoformat()
        date_to = form.cleaned_data["date_to"].isoformat()
        reason = form.cleaned_data.get("reason") or ""

        if is_staff:
            employee_id = int(form.cleaned_data["employee_id"])
        else:
            if not hasattr(request.user, "profile") or not request.user.profile.odoo_employee_id:
                messages.error(request, "Votre compte n'est pas lié à un employé Odoo.")
                return redirect("employee_home")
            employee_id = int(request.user.profile.odoo_employee_id)

        try:
            leave_id = create_leave(employee_id, leave_type_id, date_from, date_to, reason)
            messages.success(request, f"Demande envoyée ✅ (ID: {leave_id})")
            return redirect("liste_conges" if is_staff else "mes_conges")

        except Fault as e:
            # ✅ نفس منطقك السابق: إذا ما عنده allocation
            if "aucune attribution" in str(e).lower():
                messages.error(
                    request,
                    "Vous n’avez aucune attribution pour ce type de congé. "
                    "Veuillez créer une attribution (Allocation) avant de soumettre la demande."
                )
                if is_staff:
                    return redirect(f"/allocations/nouvelle/?employee_id={employee_id}&leave_type_id={leave_type_id}")
                else:
                    # الموظف ما عنده حق الإنشاء: فقط يرجع ويطلب من المدير
                    return redirect("mes_conges")
            else:
                messages.error(request, f"Erreur Odoo: {e}")

    return render(request, "portail/demander_conge.html", {"form": form, "is_staff": is_staff})


# ==========================
# APPROUVER CONGE
# ==========================
@login_required
@manager_required
@require_http_methods(["POST"])
def approuver_conge(request, leave_id):
    approve_leave(leave_id)
    messages.success(request, "Congé approuvé ✅")
    return redirect("liste_conges")


# ==========================
# REFUSER CONGE
# ==========================
@login_required
@manager_required
@require_http_methods(["POST"])
def refuser_conge(request, leave_id):
    refuse_leave(leave_id)
    messages.warning(request, "Congé refusé")
    return redirect("liste_conges")


# ==========================
# LISTE ALLOCATIONS
# ==========================
@login_required
@manager_required
def liste_allocations(request):
    allocations = get_allocations()
    return render(request, "portail/liste_allocations.html", {"allocations": allocations})


@login_required
@manager_required
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
@manager_required
@require_http_methods(["POST"])
def approuver_allocation(request, allocation_id):
    approve_allocation(allocation_id)
    messages.success(request, "Allocation validée ✅")
    return redirect("liste_allocations")


# ==========================
# REFUSER ALLOCATION
# ==========================
@login_required
@manager_required
@require_http_methods(["POST"])
def refuser_allocation(request, allocation_id):
    refuse_allocation(allocation_id)
    messages.warning(request, "Allocation refusée ⚠️")
    return redirect("liste_allocations")

@user_passes_test(is_manager)
@login_required
def dashboard(request):
    prof = request.user.profile

    if prof.role == "employee":
        return redirect("employee_home")

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

@login_required
def force_password_change(request):
    if request.method == "POST":
        p1 = request.POST.get("password1", "")
        p2 = request.POST.get("password2", "")

        if len(p1) < 6:
            messages.error(request, "Mot de passe trop court (min 6).")
        elif p1 != p2:
            messages.error(request, "Les deux mots de passe ne correspondent pas.")
        else:
            request.user.set_password(p1)
            request.user.save()

            update_session_auth_hash(request, request.user)


            prof = request.user.profile
            prof.force_password_change = False
            prof.save()

            messages.success(request, "Mot de passe modifié ✅")
            return redirect("dashboard")

    return render(request, "portail/force_password_change.html")




def _slug_username(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9._-]+", "", (name or "").strip().lower())
    return base or "user"

@staff_member_required
@transaction.atomic
def creer_employe_et_compte(request):
    jobs = get_jobs()
    job_choices = [("", "— Sélectionner —")] + [(str(j["id"]), j["name"]) for j in jobs]

    if request.method == "POST":
        form = CreateEmployeePortalForm(request.POST)
        form.fields["job_id"].choices = job_choices

        if form.is_valid():
            name = (form.cleaned_data["name"] or "").strip()
            work_email = (form.cleaned_data["work_email"] or "").strip()
            work_phone = (form.cleaned_data["work_phone"] or "").strip()
            job_id = form.cleaned_data.get("job_id") or None

            # 1) Create employee in Odoo (job_id)
            emp_id = create_employee(
                name=name,
                work_email=work_email,
                work_phone=work_phone,
                job_id=int(job_id) if job_id else None,
                department_id=None,
            )

            # 2) Create Django user
            base = _slug_username(name)
            username = base
            i = 1
            while User.objects.filter(username=username).exists():
                i += 1
                username = f"{base}{i}"

            default_password = f"{name}{name}"
            user = User.objects.create_user(username=username, password=default_password)

            Profile.objects.create(
                user=user,
                odoo_employee_id=int(emp_id),
                force_password_change=True,
                role="employee"
            )

            messages.success(
                request,
                f"Employé créé dans Odoo ✅ (ID {emp_id}) | Compte portail ✅ "
                f"| Login: {username} | Mot de passe: (Nom+Nom)"
            )
            return redirect("liste_employes")

    else:
        form = CreateEmployeePortalForm()
        form.fields["job_id"].choices = job_choices

    return render(request, "portail/creer_employe_compte.html", {"form": form})

@login_required
def employee_home(request):
    prof = request.user.profile
    emp_id = prof.odoo_employee_id


    leaves = [l for l in get_leaves() if (l.get("employee_id") and l["employee_id"][0] == emp_id)]

    return render(request, "portail/employee_home.html", {
        "leaves": leaves,
    })

@login_required
def employee_home(request):

    if request.user.is_staff:
        return redirect("dashboard")
    return render(request, "portail/employee_home.html")


@login_required
def mes_conges(request):

    prof = request.user.profile
    emp_id = prof.odoo_employee_id

    leaves = get_leaves()
    my_leaves = [l for l in leaves if (l.get("employee_id") and l["employee_id"][0] == emp_id)]
    return render(request, "portail/mes_conges.html", {"leaves": my_leaves})