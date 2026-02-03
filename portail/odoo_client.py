import xmlrpc.client

# Paramètres Odoo
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo_db"
ODOO_USERNAME = "admin"
ODOO_PASSWORD = "1234"


def odoo_login():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise Exception("Impossible de se connecter à Odoo. Vérifiez DB/login/password.")
    return uid


def odoo_models():
    return xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


# EMPLOYES
def get_employees():
    uid = odoo_login()
    models = odoo_models()

    fields = ["name", "job_title", "work_email", "work_phone", "department_id"]

    employees = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.employee", "search_read",
        [[]],
        {"fields": fields, "limit": 200}
    )
    return employees


def get_employee_by_id(emp_id):
    uid = odoo_login()
    models = odoo_models()

    fields = ["name", "job_title", "work_email", "work_phone", "department_id"]

    emp = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.employee", "read",
        [[emp_id]],
        {"fields": fields}
    )
    return emp[0] if emp else None


# TYPES DE CONGES
def get_leave_types():
    uid = odoo_login()
    models = odoo_models()

    leave_types = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave.type", "search_read",
        [[]],
        {"fields": ["name"], "limit": 200}
    )
    return leave_types


# LISTE DES CONGES
def get_leaves():
    uid = odoo_login()
    models = odoo_models()

    fields = ["employee_id", "holiday_status_id", "request_date_from", "request_date_to", "state"]

    leaves = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave", "search_read",
        [[]],
        {"fields": fields, "limit": 200}
    )
    return leaves


# CREER DEMANDE CONGE (hr.leave)
def create_leave(employee_id, leave_type_id, date_from, date_to, reason):
    uid = odoo_login()
    models = odoo_models()

    vals = {
        "employee_id": int(employee_id),
        "holiday_status_id": int(leave_type_id),
        "request_date_from": date_from,
        "request_date_to": date_to,
        "name": reason,
    }

    leave_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave", "create",
        [vals]
    )
    return leave_id


# APPROUVER / REFUSER CONGE
def approve_leave(leave_id):
    uid = odoo_login()
    models = odoo_models()

    # action_approve
    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave", "action_approve",
        [[int(leave_id)]]
    )


def refuse_leave(leave_id):
    uid = odoo_login()
    models = odoo_models()

    # action_refuse
    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave", "action_refuse",
        [[int(leave_id)]]
    )


# CREER ALLOCATION

def create_allocation(employee_id, leave_type_id, number_of_days, description):
    uid = odoo_login()
    models = odoo_models()

    vals = {
        "employee_id": int(employee_id),
        "holiday_status_id": int(leave_type_id),
        "number_of_days": float(number_of_days),
        "name": description,
    }

    allocation_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave.allocation", "create",
        [vals]
    )
    return allocation_id


# LISTE DES ALLOCATIONS (Attributions)
def get_allocations():
    uid = odoo_login()
    models = odoo_models()

    fields = ["employee_id", "holiday_status_id", "number_of_days", "state", "name", "create_date"]

    allocations = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave.allocation", "search_read",
        [[]],
        {"fields": fields, "limit": 200}
    )
    return allocations


# APPROUVER (VALIDER) UNE ALLOCATION
def approve_allocation(allocation_id):
    uid = odoo_login()
    models = odoo_models()

    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave.allocation", "action_approve",
        [[int(allocation_id)]]
    )


# REFUSER UNE ALLOCATION
def refuse_allocation(allocation_id):
    uid = odoo_login()
    models = odoo_models()

    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave.allocation", "action_refuse",
        [[int(allocation_id)]]
    )
