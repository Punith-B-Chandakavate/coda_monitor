from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/summary/', views.api_summary, name='api_summary'),
    path('api/documents/', views.api_documents, name='api_documents'),
    path('api/issues/', views.api_issues, name='api_issues'),
    path('api/remediate/', views.api_remediate, name='api_remediate'),
    path('api/trigger-scan/', views.api_trigger_scan, name='api_trigger_scan'),
    path('api/document/<int:doc_id>/', views.api_document_detail, name='api_document_detail'),
]