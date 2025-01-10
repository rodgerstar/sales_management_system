"""
URL configuration for salesMs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from main import views

urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),

    path('payment/', views.process_payment, name='process_payment'),

    path('make/payment/<int:transaction_id>', views.make_payment, name='make_payment'),
    path('agent/<int:agent_id>/', views.agent_details, name='agent_details'),
    path('goods/distributed', views.distributed_goods, name='distributed_goods'),
    path('add/goods', views.add_goods, name='add_goods'),
    path('agent/dashboard/payment', views.agent_dashboard_payment, name='agent_dashboard_payment'),
    path('goods', views.goods, name='goods'),
    path('agent', views.agent, name='agent'),
    path('add/agent', views.add_agent, name='add_agent'),
    path('pie-chart', views.pie_chart, name='pie_chart'),
    path('line-chart', views.line_chart, name='line_chart'),
    path('bar-chart', views.bar_chart, name='bar_chart'),
    path('login', views.login_page, name='login'),
    path('sign-in', views.agent_signup, name='register'),
    path('sign-out', views.user_logout, name='user_logout'),
    path('agent/reports', views.agent_reports, name='agent_reports'),
    path('general/reports', views.general_reports, name='general_reports'),
    path('outstanding/', views.outstanding_balances, name='outstanding_balances'),
    path('admin/', admin.site.urls),
]
