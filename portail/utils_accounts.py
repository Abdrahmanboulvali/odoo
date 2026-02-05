import re
from django.contrib.auth.models import User
from django.db import transaction
from .models import Profile

def slug_username(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9._-]+", "", (name or "").strip().lower())
    return base or "user"

@transaction.atomic
def create_employee_user(odoo_employee_id: int, employee_name: str) -> User:

    if Profile.objects.filter(odoo_employee_id=odoo_employee_id).exists():
        raise ValueError("Ce salarié a déjà un compte portail.")

    base = slug_username(employee_name)
    username = base
    i = 1
    while User.objects.filter(username=username).exists():
        i += 1
        username = f"{base}{i}"

    raw = (employee_name or "").strip()
    default_password = f"{raw}{raw}"

    user = User.objects.create_user(
        username=username,
        password=default_password,
        first_name=raw[:150],
    )

    Profile.objects.create(
        user=user,
        odoo_employee_id=int(odoo_employee_id),
        force_password_change=True
    )
    return user
