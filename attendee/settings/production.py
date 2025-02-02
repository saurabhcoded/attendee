from .base import *

DEBUG = False
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    ),
}

#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SECURE_SSL_REDIRECT = False
#SECURE_HSTS_SECONDS = 60
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@mail.attendee.dev'

ADMINS = []

if os.getenv('ERROR_REPORTS_RECEIVER_EMAIL_ADDRESS'):
    ADMINS.append(('Attendee Error Reports Email Receiver', os.getenv('ERROR_REPORTS_RECEIVER_EMAIL_ADDRESS')))

SERVER_EMAIL = 'noreply@mail.attendee.dev'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Set Django framework logging to DEBUG
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # This will log all SQL queries
            'propagate': False,
        },
        'attendee': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}