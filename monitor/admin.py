from django.contrib import admin
from .models import CodaDocument, DetectedIssue, ScanLog

@admin.register(CodaDocument)
class CodaDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'doc_id', 'updated_at', 'last_scanned']
    search_fields = ['name', 'doc_id']

@admin.register(DetectedIssue)
class DetectedIssueAdmin(admin.ModelAdmin):
    list_display = ['pattern_type', 'severity', 'status', 'document', 'detected_at']
    list_filter = ['severity', 'status', 'pattern_type']
    search_fields = ['detected_value']

@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ['scan_start', 'status', 'documents_scanned', 'issues_found']
    list_filter = ['status']