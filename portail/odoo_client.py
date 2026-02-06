import xmlrpc.client
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

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


# ============================================================================
# EXISTING FUNCTIONS (FROM YOUR ORIGINAL CODE)
# ============================================================================

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
    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.leave", "action_approve",
        [[int(leave_id)]]
    )


def refuse_leave(leave_id):
    uid = odoo_login()
    models = odoo_models()
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


def create_employee(
        name: str,
        work_email: str = "",
        work_phone: str = "",
        job_id: int | None = None,
        department_id: int | None = None
):
    uid = odoo_login()
    models = odoo_models()
    vals = {"name": name}
    if work_email:
        vals["work_email"] = work_email
    if work_phone:
        vals["work_phone"] = work_phone
    if job_id:
        vals["job_id"] = int(job_id)
    if department_id:
        vals["department_id"] = int(department_id)
    emp_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.employee", "create",
        [vals]
    )
    return emp_id


def get_jobs():
    uid = odoo_login()
    models = odoo_models()
    jobs = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        "hr.job", "search_read",
        [[["active", "=", True]]],
        {"fields": ["id", "name"], "limit": 500, "order": "name asc"}
    )
    return jobs


# ============================================================================
# 🚀 NEW FUNCTIONS FOR DASHBOARD ANALYTICS
# ============================================================================

# ============================================================================
# ATTENDANCE DATA (hr.attendance)
# ============================================================================

def get_attendance_records(
        employee_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch attendance records from Odoo.
    Returns empty list if hr.attendance model doesn't exist.
    """
    try:
        uid = odoo_login()
        models = odoo_models()

        domain = []
        if employee_id:
            domain.append(["employee_id", "=", int(employee_id)])
        if date_from:
            domain.append(["check_in", ">=", f"{date_from} 00:00:00"])
        if date_to:
            domain.append(["check_in", "<=", f"{date_to} 23:59:59"])

        fields = ["employee_id", "check_in", "check_out", "worked_hours"]

        attendances = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "hr.attendance", "search_read",
            [domain],
            {"fields": fields, "limit": 1000, "order": "check_in desc"}
        )
        return attendances
    except Exception as e:
        # Model doesn't exist or error - return empty list
        print(f"Attendance module not available: {e}")
        return []


def get_attendance_this_week(employee_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get attendance records for current week (Monday to Sunday)."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    return get_attendance_records(
        employee_id=employee_id,
        date_from=start_of_week.strftime("%Y-%m-%d"),
        date_to=end_of_week.strftime("%Y-%m-%d")
    )


def get_attendance_this_month(employee_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get attendance records for current month."""
    today = datetime.now()
    start_of_month = today.replace(day=1)

    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    return get_attendance_records(
        employee_id=employee_id,
        date_from=start_of_month.strftime("%Y-%m-%d"),
        date_to=end_of_month.strftime("%Y-%m-%d")
    )


# ============================================================================
# CONTRACT DATA (hr.contract) - OPTIONAL
# ============================================================================

def get_contracts(
        employee_id: Optional[int] = None,
        state: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch contract data from Odoo.
    Returns empty list if hr.contract model doesn't exist.
    """
    try:
        uid = odoo_login()
        models = odoo_models()

        domain = []
        if employee_id:
            domain.append(["employee_id", "=", int(employee_id)])
        if state:
            domain.append(["state", "=", state])

        fields = ["employee_id", "name", "wage", "date_start", "date_end", "state", "job_id", "department_id"]

        contracts = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "hr.contract", "search_read",
            [domain],
            {"fields": fields, "limit": 500, "order": "date_start desc"}
        )
        return contracts
    except Exception as e:
        # Model doesn't exist or error - return empty list
        print(f"Contract module not available: {e}")
        return []


def get_active_contracts() -> List[Dict[str, Any]]:
    """Get all active contracts (state='open'). Returns [] if module not available."""
    return get_contracts(state="open")


def get_employee_current_contract(employee_id: int) -> Optional[Dict[str, Any]]:
    """Get the current active contract for a specific employee."""
    contracts = get_contracts(employee_id=employee_id, state="open")
    return contracts[0] if contracts else None


# ============================================================================
# 📊 KPI CALCULATION FUNCTIONS
# ============================================================================

def calculate_total_hours_worked(
        employee_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
) -> float:
    """Calculate total hours worked for given period."""
    attendances = get_attendance_records(employee_id, date_from, date_to)
    total_hours = sum(att.get("worked_hours", 0.0) for att in attendances)
    return round(total_hours, 2)


def calculate_hours_this_week(employee_id: Optional[int] = None) -> float:
    """Calculate total hours worked this week."""
    attendances = get_attendance_this_week(employee_id)
    total_hours = sum(att.get("worked_hours", 0.0) for att in attendances)
    return round(total_hours, 2)


def calculate_absenteeism_rate(
        employee_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        expected_hours_per_week: float = 40.0
) -> Dict[str, Any]:
    """Calculate absenteeism rate based on attendance vs expected hours."""
    if not date_from or not date_to:
        today = datetime.now()
        date_from = today.replace(day=1).strftime("%Y-%m-%d")
        if today.month == 12:
            date_to = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            date_to = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        date_to = date_to.strftime("%Y-%m-%d")

    actual_hours = calculate_total_hours_worked(employee_id, date_from, date_to)

    start = datetime.strptime(date_from, "%Y-%m-%d")
    end = datetime.strptime(date_to, "%Y-%m-%d")
    days = (end - start).days + 1
    weeks = days / 7.0
    expected_hours = weeks * expected_hours_per_week

    absent_hours = max(0, expected_hours - actual_hours)
    rate_percent = (absent_hours / expected_hours * 100) if expected_hours > 0 else 0.0

    return {
        "actual_hours": round(actual_hours, 2),
        "expected_hours": round(expected_hours, 2),
        "absent_hours": round(absent_hours, 2),
        "rate_percent": round(rate_percent, 2),
        "period_days": days
    }


def calculate_salary_mass(department_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Calculate total salary mass from active contracts.
    Returns zeros if contract module not available.
    """
    contracts = get_active_contracts()

    if department_id:
        contracts = [
            c for c in contracts
            if c.get("department_id") and c["department_id"][0] == department_id
        ]

    total_wage = sum(c.get("wage", 0.0) for c in contracts)
    employee_count = len(contracts)
    average_wage = (total_wage / employee_count) if employee_count > 0 else 0.0

    return {
        "total_monthly_wage": round(total_wage, 2),
        "employee_count": employee_count,
        "average_wage": round(average_wage, 2)
    }


def get_salary_evolution(months: int = 6) -> List[Dict[str, Any]]:
    """Get salary mass evolution over past N months."""
    today = datetime.now()
    evolution = []

    for i in range(months):
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")

        salary_data = calculate_salary_mass()

        evolution.append({
            "month": month_str,
            "total_wage": salary_data["total_monthly_wage"],
            "employee_count": salary_data["employee_count"]
        })

    return list(reversed(evolution))


def get_leave_balance_for_employee(employee_id: int) -> Dict[int, Dict[str, Any]]:
    """Calculate leave balance per leave type for an employee."""
    all_allocations = get_allocations()
    employee_allocations = [
        a for a in all_allocations
        if a.get("employee_id") and a["employee_id"][0] == employee_id
           and a.get("state") in ["validate", "validated"]
    ]

    all_leaves = get_leaves()
    employee_leaves = [
        l for l in all_leaves
        if l.get("employee_id") and l["employee_id"][0] == employee_id
           and l.get("state") in ["validate", "validated"]
    ]

    balance = {}

    for alloc in employee_allocations:
        leave_type_id = alloc["holiday_status_id"][0]
        leave_type_name = alloc["holiday_status_id"][1]

        if leave_type_id not in balance:
            balance[leave_type_id] = {
                "name": leave_type_name,
                "allocated": 0.0,
                "taken": 0.0,
                "remaining": 0.0
            }

        balance[leave_type_id]["allocated"] += alloc.get("number_of_days", 0.0)

    for leave in employee_leaves:
        leave_type_id = leave["holiday_status_id"][0]
        leave_type_name = leave["holiday_status_id"][1]

        if leave_type_id not in balance:
            balance[leave_type_id] = {
                "name": leave_type_name,
                "allocated": 0.0,
                "taken": 0.0,
                "remaining": 0.0
            }

        if leave.get("request_date_from") and leave.get("request_date_to"):
            date_from = datetime.strptime(leave["request_date_from"], "%Y-%m-%d")
            date_to = datetime.strptime(leave["request_date_to"], "%Y-%m-%d")
            days_taken = (date_to - date_from).days + 1
            balance[leave_type_id]["taken"] += days_taken

    for leave_type_id in balance:
        balance[leave_type_id]["remaining"] = (
                balance[leave_type_id]["allocated"] - balance[leave_type_id]["taken"]
        )

    return balance


# ============================================================================
# 📈 DASHBOARD DATA AGGREGATORS
# ============================================================================

def get_manager_dashboard_data() -> Dict[str, Any]:
    """Aggregate all data needed for manager dashboard."""
    employees = get_employees()
    leaves = get_leaves()
    allocations = get_allocations()

    total_employees = len(employees)
    pending_leaves = [l for l in leaves if l.get("state") in ["confirm", "validate1"]]
    approved_leaves = [l for l in leaves if l.get("state") in ["validate", "validated"]]
    pending_allocations = [a for a in allocations if a.get("state") in ["draft", "confirm"]]

    # Advanced KPIs - with error handling
    absenteeism = calculate_absenteeism_rate()
    salary_data = calculate_salary_mass()
    salary_evolution = get_salary_evolution(months=6)

    recent_leaves = sorted(leaves, key=lambda x: x.get("id", 0), reverse=True)[:5]
    recent_allocations = sorted(allocations, key=lambda x: x.get("id", 0), reverse=True)[:5]

    return {
        "total_employees": total_employees,
        "pending_leaves_count": len(pending_leaves),
        "approved_leaves_count": len(approved_leaves),
        "pending_allocations_count": len(pending_allocations),
        "absenteeism_rate": absenteeism["rate_percent"],
        "absenteeism_details": absenteeism,
        "salary_mass": salary_data["total_monthly_wage"],
        "salary_details": salary_data,
        "salary_evolution": salary_evolution,
        "recent_leaves": recent_leaves,
        "recent_allocations": recent_allocations
    }


def get_employee_dashboard_data(employee_id: int) -> Dict[str, Any]:
    """Aggregate all data needed for employee dashboard."""
    employee = get_employee_by_id(employee_id)

    hours_this_week = calculate_hours_this_week(employee_id)
    hours_this_month = calculate_total_hours_worked(
        employee_id=employee_id,
        date_from=datetime.now().replace(day=1).strftime("%Y-%m-%d"),
        date_to=datetime.now().strftime("%Y-%m-%d")
    )

    leave_balance = get_leave_balance_for_employee(employee_id)

    all_leaves = get_leaves()
    my_leaves = [
        l for l in all_leaves
        if l.get("employee_id") and l["employee_id"][0] == employee_id
    ]
    recent_leaves = sorted(my_leaves, key=lambda x: x.get("id", 0), reverse=True)[:5]

    return {
        "employee": employee,
        "hours_this_week": hours_this_week,
        "hours_this_month": hours_this_month,
        "leave_balance": leave_balance,
        "recent_leaves": recent_leaves,
        "total_leave_types": len(leave_balance)
    }