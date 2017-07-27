from flask import Blueprint, jsonify, request, Response
from github import get, compute, get_from_cache
import json

gf = Blueprint('gf', __name__)

topics = ["forks", "last_updated", "open_issues", "stars", "watchers"]

@gf.route('/')
def index():
    (data, status, headers) = _cache("/")
    return _construct_response(content=data, status_code=status, headers={'Content-Type': headers})

@gf.route('/<path:path>')
def proxy(path):
    (data, status, headers) = _cache(request.path)
    return _construct_response(content=data, status_code=status, headers={'Content-Type': headers})

@gf.route('/view/top/<int:n>/<topic>')
def top_n_for_topic(n, topic):
    if topic in topics:
        (data, status, headers) = _compute(request.path, n, topic)
        return _construct_response(content=data, status_code=status, headers={'Content-Type': headers})
    else:
        return ("Not found", 404)

@gf.route('/healthcheck')
def healthcheck():
    return ("ok", 200)

# TODO: Handle correct http status codes for 404, 500 etc
def _cache(path):
    (data, status, headers) = get_from_cache(path)
    if data is None and status != 404:
        return get(path)

    return (data, status, headers)

def _compute(path, n, topic):
    (data, status, headers) = get_from_cache(path)
    if data is None and status != 404:
        return compute(path, n, topic)

    return (data, status, headers)

def _construct_response(content, status_code, headers):
    if not content:
        return Response(content, status=status_code, headers=headers)
    return Response(json.dumps(content), status=status_code, headers=headers)