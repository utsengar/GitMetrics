# GitMetrics - Github proxy with caching and predefined aggregation endpoints


## What is GitMetrics?
GitMetrics is a proxy for GitHub V3 API. It also has a caching layer build to help you with rate limits. The cache updates every hr (caches response (image, json, html etc) + status code + content type) and the TTL for cache entries is 30min. You can change it to any interval. Its build with good intentions but its not quite ready to scale yet. Please read Design Considerations on ideas of how to improve it.

## Quick Start
Prerequisite: Python 2.7. I suggest creating a virtualenv to keep your machine clean from the dependencies GitMetrics needs. Get tokens from here: https://github.com/settings/tokens

1. `export GITHUB_API_TOKEN=<your token here>` and cd to GitMetrics
2. `pip install -r requirements.txt`
3. `export FLASK_APP=app.py`
4. `flask run -p 8080` (or any other port)
5. Now check http://127.0.0.1:8080/view/top/10/stars (returns top 10 started project for `bitcoin` project)

## Design Considerations

1. *Caching:* GitMetrics caches response from gitub in memory within the application lifecycle. This is not efficient if this is deployed on multiple instances. If there is a cache miss on any node, that node will make a call to github and cache the repsonse locally. Switch from SimpleCache to MemcachedCache or Redis for before production use. It can be switched from `app.py`
2. *Periodic polling*: GitMetrics polls Github every 1hr. Again, this happens locally. For production usage this should be replaced with a worker which runs once and updates the cache. It can be solved by switching to a celery or any other task processor.
3. *Initial Bootstrap*: Gitlfix warms up the cache right after server startup. This blocks server startup for <5sec. This can be improved in multi-node deployment by using celery.

## Deployment

GitMetrics doesn't come with a deployment script, but `fabric` can be used to deploy it to machines.