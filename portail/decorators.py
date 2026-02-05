# portail/decorators.py
from django.shortcuts import redirect
from django.contrib import messages

def manager_required(view_func):
    def _wrapped(request, *args, **kwargs):
        prof = getattr(request.user, "profile", None)
        if prof and prof.role == "manager":
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé (manager uniquement).")
        return redirect("employee_home")
    return _wrapped

def employee_required(view_func):
    def _wrapped(request, *args, **kwargs):
        prof = getattr(request.user, "profile", None)
        if prof and prof.role == "employee":
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé (employé uniquement).")
        return redirect("dashboard")
    return _wrapped
