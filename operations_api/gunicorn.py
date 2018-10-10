from operations_api.config.settings import FLASK_SERVER_HOST, FLASK_SERVER_PORT

import multiprocessing

bind = "{host}:{port}".format(
    host=FLASK_SERVER_HOST,
    port=FLASK_SERVER_PORT,
)
timeout = 180
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
