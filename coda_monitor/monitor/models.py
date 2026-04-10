from django.db import models


class CodaDocument(models.Model):
    doc_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=500)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    browser_link = models.URLField(max_length=1000)
    last_scanned = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class DetectedIssue(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('IGNORED', 'Ignored'),
    ]

    document = models.ForeignKey(CodaDocument, on_delete=models.CASCADE, related_name='issues')
    table_name = models.CharField(max_length=500)
    row_id = models.CharField(max_length=100)
    column_name = models.CharField(max_length=200)
    detected_value = models.TextField()
    pattern_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-severity', '-detected_at']

    def __str__(self):
        return f"{self.pattern_type} in {self.document.name} - {self.table_name}"


class ScanLog(models.Model):
    scan_start = models.DateTimeField()
    scan_end = models.DateTimeField(null=True, blank=True)
    documents_scanned = models.IntegerField(default=0)
    issues_found = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Scan at {self.scan_start}"