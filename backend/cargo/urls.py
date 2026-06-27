from django.urls import path

from .views import CargoListView, CargoStatsView, UploadManifestView

urlpatterns = [
    path('api/v1/upload/', UploadManifestView.as_view(), name='cargo-upload'),
    path('api/v1/cargo/stats/', CargoStatsView.as_view(), name='cargo-stats'),
    path('api/v1/cargo/', CargoListView.as_view(), name='cargo-list'),
]
