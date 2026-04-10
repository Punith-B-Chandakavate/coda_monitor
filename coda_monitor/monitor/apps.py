from django.apps import AppConfig
import logging
import sys

logger = logging.getLogger(__name__)

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return

        try:
            from . import scheduler
            scheduler.start_scheduler()
            logger.info("Scheduler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")