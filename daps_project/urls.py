from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.dashboard, name='dashboard'),
    path('signup/', core_views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', core_views.profile_view, name='profile'),
    path('goal/add/', core_views.add_goal, name='add_goal'),
    path('goal/toggle/<int:goal_id>/', core_views.toggle_goal, name='toggle_goal'),
    path('request/accept/<int:request_id>/', core_views.accept_request, name='accept_request'),
]
