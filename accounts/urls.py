from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import user_login, admin_dashboard, staff_dashboard, employee_dashboard, researcher_dashboard, admin_map_dashboard


urlpatterns = [
    path('login/', user_login, name='user_login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('staff_dashboard/', staff_dashboard, name='staff_dashboard'),
    path('employee_dashboard/', employee_dashboard, name='employee_dashboard'),
    path('researcher_dashboard/', researcher_dashboard, name='researcher_dashboard'),
    path('admin_map_dashboard/', admin_map_dashboard, name='admin_map_dashboard'),
]