from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:

            allowed = [
                reverse("force_password_change"),
                reverse("logout"),
            ]
            if request.path.startswith("/admin/"):
                return self.get_response(request)

            try:
                if request.user.profile.force_password_change and request.path not in allowed:
                    return redirect("force_password_change")
            except Exception:
                pass

        return self.get_response(request)
