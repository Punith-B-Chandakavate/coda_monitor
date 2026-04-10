from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import sys

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    """Start the background scheduler for periodic scans"""
    # Skip if running migrations
    if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
        return

    try:
        from .tasks import scan_all_documents

        # Schedule the scan job every hour
        scheduler.add_job(
            scan_all_documents,
            trigger=IntervalTrigger(hours=1),
            id='scan_documents',
            name='Scan all Coda documents for sensitive data',
            replace_existing=True
        )

        scheduler.start()
        logger.info("Scheduler started - scans will run every hour")

        # Run initial scan after 10 seconds
        from django.utils import timezone
        scheduler.add_job(
            scan_all_documents,
            'date',
            run_date=timezone.now(),
            id='initial_scan',
            replace_existing=True
        )
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")