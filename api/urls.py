from django.urls import include, path

from api.v1.urls import urlpatterns_v1

app_name = "api"

urlpatterns = [
    path("v1/", include(urlpatterns_v1)),
]
