import logging
from datetime import datetime
from django.utils import timezone
from .models import CodaDocument, DetectedIssue, ScanLog
from .utils.coda_client import CodaAPIClient
from .utils.pattern_detector import PatternDetector
from .utils.alert_service import AlertService

logger = logging.getLogger(__name__)


def scan_all_documents():
    scan_log = ScanLog.objects.create(
        scan_start=timezone.now(),
        status='RUNNING'
    )

    try:
        client = CodaAPIClient()
        detector = PatternDetector()
        alert_service = AlertService()

        docs_data = client.list_documents()
        logger.info(f"Found {len(docs_data)} documents to scan")

        total_issues = 0

        for doc_data in docs_data:
            try:
                doc, created = CodaDocument.objects.update_or_create(
                    doc_id=doc_data['id'],
                    defaults={
                        'name': doc_data['name'],
                        'created_at': datetime.fromisoformat(doc_data['createdAt'].replace('Z', '+00:00')),
                        'updated_at': datetime.fromisoformat(doc_data['updatedAt'].replace('Z', '+00:00')),
                        'is_published': doc_data.get('isPublished', False),
                        'browser_link': doc_data.get('browserLink', ''),
                        'last_scanned': timezone.now()
                    }
                )

                issues = scan_document_sync(doc.doc_id)
                total_issues += len(issues)

                for issue in issues:
                    if issue.severity in ['HIGH', 'CRITICAL']:
                        alert_service.notify_issue_detected({
                            'document_name': doc.name,
                            'table_name': issue.table_name,
                            'column_name': issue.column_name,
                            'pattern_type': issue.pattern_type,
                            'severity': issue.severity,
                            'detected_value': issue.detected_value
                        })

                logger.info(f"Scanned {doc.name}: found {len(issues)} issues")

            except Exception as e:
                logger.error(f"Error scanning {doc_data.get('id')}: {e}")
                continue

        scan_log.documents_scanned = len(docs_data)
        scan_log.issues_found = total_issues
        scan_log.scan_end = timezone.now()
        scan_log.status = 'COMPLETED'
        scan_log.save()

        logger.info(f"Scan completed: {total_issues} issues found")

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        scan_log.status = 'FAILED'
        scan_log.error_message = str(e)
        scan_log.scan_end = timezone.now()
        scan_log.save()


def scan_document_sync(doc_id: str):
    client = CodaAPIClient()
    detector = PatternDetector()

    try:
        doc = CodaDocument.objects.get(doc_id=doc_id)
        tables = client.list_tables(doc_id)

        all_issues = []

        for table in tables:
            table_id = table['id']
            table_name = table['name']
            rows = client.get_table_rows(doc_id, table_id)
            issues = detector.scan_table_rows(rows)

            for issue_data in issues:
                issue, created = DetectedIssue.objects.update_or_create(
                    document=doc,
                    table_name=table_name,
                    row_id=issue_data['row_id'],
                    column_name=issue_data['column_name'],
                    pattern_type=issue_data['pattern_type'],
                    defaults={
                        'detected_value': issue_data['detected_value'],
                        'severity': issue_data['severity'],
                        'status': 'OPEN'
                    }
                )
                all_issues.append(issue)

        doc.last_scanned = timezone.now()
        doc.save()
        return all_issues

    except Exception as e:
        logger.error(f"Error scanning document {doc_id}: {e}")
        raise


def remediate_issue_sync(issue_id: int, action: str, note: str = ""):
    """Remediate a detected issue"""
    try:
        from monitor.models import DetectedIssue

        issue = DetectedIssue.objects.get(id=issue_id)

        # Store old status for logging
        old_status = issue.status

        if action == 'resolve':
            issue.status = 'RESOLVED'
            issue.resolved_at = timezone.now()
        elif action == 'ignore':
            issue.status = 'IGNORED'
        elif action == 'in_progress':
            issue.status = 'IN_PROGRESS'

        issue.resolution_note = note
        issue.save()

        # Prepare issue details for Slack
        issue_details = {
            'document_name': issue.document.name,
            'pattern_type': issue.pattern_type,
            'severity': issue.severity,
            'table_name': issue.table_name,
            'column_name': issue.column_name,
            'detected_value': issue.detected_value[:100]
        }

        # Send alert about remediation
        alert_service = AlertService()
        result = alert_service.notify_remediation({
            'action': action,
            'issue_id': issue_id,
            'new_status': issue.status,
            'old_status': old_status,
            'note': note,
            'issue_details': issue_details
        })

        logger.info(f"Issue {issue_id} remediated with action: {action} - Slack notified: {result}")
        return True

    except Exception as e:
        logger.error(f"Failed to remediate issue {issue_id}: {e}")
        return False