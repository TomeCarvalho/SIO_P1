"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app_insec import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wiki/', views.dashboard),
    path('', views.go_to_dashboard),
    path('wiki/<int:i>/', views.wiki_page),
    path('wiki/<int:_id>/comment', views.create_comment),
    path('wiki/create/', views.create_wiki),
    path('login/', views.login_page),
    path('createaccount/', views.create_account),
    path('logout/', views.logout),
    path('deletepage/', views.delete_page),
    path('deletecomment/', views.delete_comment),
    path('profile', views.profile),
    path('profile/changepassword', views.change_password)
]
