import heapq
import calendar
import requests
from app import cache, GITHUB_BASE, GITHUB_API_TOKEN, CACHE_TTL
from datetime import datetime
from flask import Response

headers = {"Accept": "application/vnd.github.v3+json", "Authorization" : "token " + GITHUB_API_TOKEN}

def get_from_cache(resource):
    data = cache.get("data+" + resource)
    headers = cache.get("headers+" + resource)
    status = cache.get("status+" + resource)
    return (data, status, headers)

def get(resource):
    try:
        resp = requests.get("{0}{1}".format(GITHUB_BASE, resource), headers=headers)
        result = []
        if resp.status_code == 200:
            result = resp.json()
            while resp.links.has_key("next"):
                next_link = resp.links['next']
                resp = requests.get(next_link["url"], headers=headers)
                result.extend(resp.json())
            r = result
        else:
            r = None
    except requests.exceptions.ConnectionError:
        r = {"message": "Connection refused"}
    except ValueError:
        r = resp.text

    cached_resources = cache.get("resources_to_cache")
    if resource not in cached_resources:
        cached_resources.append(resource)
        cache.set("data+"+resource, r, timeout=CACHE_TTL)
        cache.set("headers+"+resource, resp.headers.get("content-type"), timeout=CACHE_TTL)
        cache.set("status+"+resource, resp.status_code, timeout=CACHE_TTL)
        cache.set("resources_to_cache", cached_resources, timeout=CACHE_TTL)

    return (r, resp.status_code, resp.headers.get("content-type"))

def compute(path, n, topic):
    h_forks = []
    h_last_updated = []
    h_open_issues = []
    h_stars = []
    h_watchers = []
    repo_data = cache.get("data+/orgs/bitcoin/repos")
    if not repo_data:
        repo_data = get("/orgs/bitcoin/repos")[0]
    for repo in repo_data:
        if topic == "forks":
            heapq.heappush(h_forks, (repo["forks"], [repo['full_name'], repo["forks"]]))
        elif topic == "last_updated":
            heapq.heappush(h_last_updated, (iso8601_to_epoch(repo["updated_at"]), [repo['full_name'], repo["updated_at"]]))
        elif topic == "open_issues":
            heapq.heappush(h_open_issues, (repo["open_issues_count"], [repo['full_name'], repo["open_issues_count"]]))
        elif topic == "stars":
            heapq.heappush(h_stars, (repo["stargazers_count"], [repo['full_name'], repo["stargazers_count"]]))
        elif topic == "watchers":
            heapq.heappush(h_watchers, (repo["watchers"], [repo['full_name'], repo["watchers"]]))

    if topic == "forks":
        largest = heapq.nlargest(n, h_forks)
    elif topic == "last_updated":
        largest = heapq.nlargest(n, h_last_updated)
    elif topic == "open_issues":
        largest = heapq.nlargest(n, h_open_issues)
    elif topic == "stars":
        largest = heapq.nlargest(n, h_stars)
    elif topic == "watchers":
        largest = heapq.nlargest(n, h_watchers)
    
    largest = [x[1] for x in largest]
    cache.set("data+"+path, largest, timeout=CACHE_TTL)
    return (largest, 200, {})

def iso8601_to_epoch(datestring):
    return calendar.timegm(datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%SZ").timetuple())
