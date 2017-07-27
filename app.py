from flask import Flask
from werkzeug.contrib.cache import SimpleCache
from flask_apscheduler import APScheduler
from apscheduler.triggers.date import DateTrigger
import logging
import datetime
import os

GITHUB_BASE = "https://api.github.com"
CACHE_TTL = 30 * 60

class Config(object):
    JOBS = [
        {
            'id': 'pull',
            'func': 'jobs:get_data_async',
            'args': '',
            'trigger': 'interval',
            'hours': 1
        },
        {
            'id': 'compute',
            'func': 'jobs:compute_stats_async',
            'args': '',
            'trigger': 'interval',
            'hours': 1
        }
    ]


app = Flask(__name__)
app.config.from_object(Config())
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN')

cache = SimpleCache()
cache.set("resources_to_cache", ["/orgs/bitcoin", "/orgs/bitcoin/members", "/orgs/bitcoin/repos"])

logging.basicConfig()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from gitmetrics import gf
app.register_blueprint(gf)

def _run_on_start():
    from jobs import get_data_async, compute_stats_async
    get_data_async()
    compute_stats_async()

_run_on_start()