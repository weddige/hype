import requests


def get_trending_statuses(instance_name):
    return requests.get(
        f"https://{instance_name}/api/pixelfed/v2/discover/posts/trending?range=daily"
    ).json()
