from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    
    # EMPLOYES
    path("employes/", views.liste_employes, name="liste_employes"),
    path("employes/<int:emp_id>/", views.fiche_employe, name="fiche_employe"),

    # CONGES
    path("conges/", views.liste_conges, name="liste_conges"),
    path("conges/demande/", views.demander_conge, name="demander_conge"),

    path("conges/<int:leave_id>/approve/", views.approuver_conge, name="approve_leave"),
    path("conges/<int:leave_id>/refuse/", views.refuser_conge, name="refuse_leave"),

    # ALLOCATIONS (NOUVEAU)
    path("allocations/nouvelle/", views.creer_allocation, name="creer_allocation"),
    path("allocations/", views.liste_allocations, name="liste_allocations"),
    path("allocations/<int:allocation_id>/approve/", views.approuver_allocation, name="approve_allocation"),
    path("allocations/<int:allocation_id>/refuse/", views.refuser_allocation, name="refuse_allocation"),

    path("accounts/force-password/", views.force_password_change, name="force_password_change"),
    path("employes/nouveau/", views.creer_employe_et_compte, name="creer_employe_et_compte"),
    path("employee/", views.employee_home, name="employee_home"),
    path("mes-conges/", views.mes_conges, name="mes_conges"),


]
