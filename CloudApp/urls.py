from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    #path("display", views.display, name="display"),
    path("filter_agent", views.filter_agent, name= "filter_agent"),
    path("filter_queue", views.filter_queue, name= "filter_queue"),
    path("agent_role_report", views.agent_role_report, name= "agent_role_report"),
    path("filter_agent_role", views.filter_agent_role, name= "filter_agent_role"),
    path("filter", views.filter, name= "filter"),
    path('download',views.download, name= "download"),
    path("agent_report", views.agent_report, name="agent_report"),
    path("queue_report", views.queue_report, name= "queue_report"),
    path('agent_role_report',views.agent_role_report, name= "agent_role_report")
    ]