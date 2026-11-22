"""
scheduler.py
────────────
Automated daily job that:
  1. Fetches live AQI for each historical-model city
  2. Logs the actual-vs-predicted comparison to the validation DB
  3. Stores tomorrow's fresh forecast for future comparison

Uses APScheduler BackgroundScheduler. Runs at 09:00 IST daily.
"""

import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

_scheduler = None


def _daily_validation_job():
    """
    Daily job that runs for each city with a historical model:
    1. Fetch live AQI
    2. Log validation (actual vs yesterday's prediction)
    3. Store today's forecast for tomorrow
    """
    try:
        from city_config import CITY_REGISTRY, HISTORICAL_CITIES, get_city_config
    except (ImportError, ValueError):
        try:
            from ..city_config import CITY_REGISTRY, HISTORICAL_CITIES, get_city_config
        except Exception:
            from backend.city_config import CITY_REGISTRY, HISTORICAL_CITIES, get_city_config

    from .live_aqi import get_live_aqi
    from .validation import log_daily_validation, generate_forecasts_from_dashboard
    from .main import _load_json, DASHBOARD_DATA_PATH

    logger.info("[VALIDATION] Running daily validation job...")

    # Load dashboard data for forecast generation
    dashboard_data = _load_json(DASHBOARD_DATA_PATH)

    for city_name in HISTORICAL_CITIES:
        try:
            city_config = get_city_config(city_name)
            if not city_config:
                continue

            # Fetch live AQI
            live = get_live_aqi(city_config)
            actual_aqi = live.get("consensus_aqi")

            if actual_aqi is not None:
                source = "WAQI" if live.get("waqi") else "OpenAQ"
                log_daily_validation(city_name, actual_aqi, source=source)
                logger.info(f"  ✅ {city_name}: actual AQI = {actual_aqi}")
            else:
                logger.warning(f"  ⚠️ {city_name}: could not fetch live AQI")

        except Exception as e:
            logger.error(f"  ❌ {city_name}: validation failed: {e}")

    # Store tomorrow's forecasts
    if dashboard_data:
        generate_forecasts_from_dashboard(dashboard_data)
        logger.info("  📊 Tomorrow's forecasts stored")

    logger.info("✅ Daily validation job complete")


def start_scheduler():
    """Start the APScheduler background scheduler."""
    global _scheduler

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning(
            "APScheduler not installed. Daily validation will not run automatically. "
            "Install with: pip install apscheduler"
        )
        return

    if _scheduler is not None:
        logger.info("Scheduler already running")
        return

    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # Run daily at 09:00 IST
    _scheduler.add_job(
        _daily_validation_job,
        trigger=CronTrigger(hour=9, minute=0, timezone="Asia/Kolkata"),
        id="daily_validation",
        name="Daily AQI Validation",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("[SCHEDULER] Scheduler started - daily validation at 09:00 IST")

    # Also run once at startup (after a short delay to let things initialize)
    from apscheduler.triggers.date import DateTrigger

    run_at = datetime.now(IST) + timedelta(seconds=10)
    _scheduler.add_job(
        _daily_validation_job,
        trigger=DateTrigger(run_date=run_at, timezone="Asia/Kolkata"),
        id="startup_validation",
        name="Startup Validation Run",
        replace_existing=True,
    )


def stop_scheduler():
    """Stop the scheduler if running."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
