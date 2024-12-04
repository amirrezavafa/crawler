import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN', ''),
        
        # Integrations
        integrations=[
            LoggingIntegration(
                level=logging.INFO,     # Capture info and above
                event_level=logging.ERROR  # Send error level to Sentry
            ),
            SqlalchemyIntegration()
        ],
        
        # Performance tracking
        traces_sample_rate=1.0,  # Capture 100% of transactions
        profiles_sample_rate=1.0,  # Capture 100% of performance profiles
        
        # Environment context
        environment=os.getenv('ENV', 'development'),
        release="patanjameh-crawler-v1.0.0"
    )

def add_sentry_context(extra_context=None):
    """
    Add extra context to Sentry error tracking
    """
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("crawler_type", "clothing")
        scope.set_tag("website", "patanjameh.ir")
        
        if extra_context:
            for key, value in extra_context.items():
                scope.set_extra(key, value)