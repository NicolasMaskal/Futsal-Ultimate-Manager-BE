from django.urls import include, path

urlpatterns = [
    path("auth/", include(("src.authentication.urls", "authentication"))),
    path("users/", include(("src.users.urls", "users"))),
    path("", include(("src.futsal_sim.urls", "futsal_sim"))),
]
