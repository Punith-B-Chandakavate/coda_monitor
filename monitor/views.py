from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
import threading

from .models import CodaDocument, DetectedIssue, ScanLog
from .tasks import scan_all_documents, remediate_issue_sync, scan_document_sync

logger = logging.getLogger(__name__)


def dashboard(request):
    return render(request, 'monitor/dashboard.html')


def api_summary(request):
    total_docs = CodaDocument.objects.count()
    open_issues = DetectedIssue.objects.filter(status='OPEN').count()
    critical_issues = DetectedIssue.objects.filter(status='OPEN', severity='CRITICAL').count()
    high_issues = DetectedIssue.objects.filter(status='OPEN', severity='HIGH').count()

    recent_scans = ScanLog.objects.order_by('-scan_start')[:5]
    scans_data = [{
        'scan_start': s.scan_start.isoformat(),
        'documents_scanned': s.documents_scanned,
        'issues_found': s.issues_found,
        'status': s.status
    } for s in recent_scans]

    return JsonResponse({
        'total_documents': total_docs,
        'open_issues': open_issues,
        'critical_issues': critical_issues,
        'high_issues': high_issues,
        'recent_scans': scans_data
    })


def api_documents(request):
    documents = CodaDocument.objects.all()
    docs_data = [{
        'id': doc.id,
        'doc_id': doc.doc_id,
        'name': doc.name,
        'updated_at': doc.updated_at.isoformat(),
        'last_scanned': doc.last_scanned.isoformat() if doc.last_scanned else None,
        'issue_count': doc.issues.filter(status='OPEN').count()
    } for doc in documents]

    return JsonResponse({'documents': docs_data})


def api_issues(request):
    severity = request.GET.get('severity')
    status = request.GET.get('status', 'OPEN')
    document_id = request.GET.get('document_id')

    queryset = DetectedIssue.objects.filter(status=status)

    if severity:
        queryset = queryset.filter(severity=severity)
    if document_id:
        queryset = queryset.filter(document_id=document_id)

    issues_data = [{
        'id': issue.id,
        'document_name': issue.document.name,
        'document_id': issue.document.id,
        'table_name': issue.table_name,
        'column_name': issue.column_name,
        'detected_value': issue.detected_value,
        'pattern_type': issue.pattern_type,
        'severity': issue.severity,
        'detected_at': issue.detected_at.isoformat(),
        'status': issue.status
    } for issue in queryset[:100]]

    return JsonResponse({'issues': issues_data})


@csrf_exempt
@require_http_methods(["POST"])
def api_remediate(request):
    try:
        data = json.loads(request.body)
        issue_id = data.get('issue_id')
        action = data.get('action')
        note = data.get('note', '')

        if not issue_id or not action:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        success = remediate_issue_sync(issue_id, action, note)

        if success:
            return JsonResponse({'success': True, 'message': 'Remediation completed'})
        else:
            return JsonResponse({'error': 'Remediation failed'}, status=500)

    except Exception as e:
        logger.error(f"Error in remediation API: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_trigger_scan(request):
    try:
        scan_thread = threading.Thread(target=scan_all_documents)
        scan_thread.start()

        return JsonResponse({'success': True, 'message': 'Scan initiated in background'})
    except Exception as e:
        logger.error(f"Error triggering scan: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def api_document_detail(request, doc_id):
    document = get_object_or_404(CodaDocument, id=doc_id)
    issues = document.issues.filter(status='OPEN')

    scan_thread = threading.Thread(target=scan_document_sync, args=(document.doc_id,))
    scan_thread.start()

    return JsonResponse({
        'id': document.id,
        'name': document.name,
        'doc_id': document.doc_id,
        'created_at': document.created_at.isoformat(),
        'updated_at': document.updated_at.isoformat(),
        'is_published': document.is_published,
        'issue_count': issues.count(),
        'issues': [{
            'id': i.id,
            'table_name': i.table_name,
            'column_name': i.column_name,
            'pattern_type': i.pattern_type,
            'severity': i.severity
        } for i in issues]
    })