from django.urls import path
from . import views

urlpatterns = [
    path("receive/", views.receive_gnss_data, name="receive_gnss_data"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("api/latest/", views.latest_gnss_data, name="latest_gnss_data"),
    path("latency-test/", views.latency_test, name="latency_test"),
]
