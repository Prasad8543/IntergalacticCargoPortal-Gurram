from django.urls import path

from .views import LoginView, LogoutView, SignupView, UserDetailView, UserListView

urlpatterns = [
    path('api/v1/signup/', SignupView.as_view(), name='signup'),
    path('api/v1/login/', LoginView.as_view(), name='login'),
    path('api/v1/logout/', LogoutView.as_view(), name='logout'),
    path('api/v1/users/', UserListView.as_view(), name='user-list'),
    path('api/v1/users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
