from app import cache
from github import get, compute

# Note: This can be further parallelized using grequests or celery
def get_data_async():
    cached_resources = cache.get("resources_to_cache")
    if not cached_resources:
    	return
    	
    for resource in cached_resources:
        (data, status, header) = get(resource)
        cache.set("data+" + resource, data)
        cache.set("headers+" + resource, header)

def compute_stats_async():
    topics = ["forks", "last_updated", "open_issues", "stars", "watchers"]

    for n in range(1, 6):
        for t in topics:
            compute("/views/" + str(n) + "/top/" + t, n, t)
