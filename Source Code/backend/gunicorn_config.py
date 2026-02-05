import multiprocessing
import os

# Server socket
bind = '0.0.0.0:' + str(os.environ.get('PORT', 5000))

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 2

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Debugging
reload = os.environ.get('FLASK_ENV') == 'development'

# Logging
errorlog = '-'  # Log to stdout
loglevel = 'info'
accesslog = '-'  # Log to stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
