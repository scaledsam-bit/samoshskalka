import os
from instagrapi import Client

SESSION_FILE = os.path.join(os.path.dirname(__file__), "data", "ig_session.json")


def _get_client() -> Client:
    cl = Client()

    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)
        cl.login(
            os.environ["IG_USERNAME"],
            os.environ["IG_PASSWORD"],
        )
    else:
        cl.login(
            os.environ["IG_USERNAME"],
            os.environ["IG_PASSWORD"],
        )
        os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
        cl.dump_settings(SESSION_FILE)

    return cl


def fetch_followers(cl: Client, user_id: str) -> set[str]:
    users = cl.user_followers(user_id, amount=0)
    return {u.username for u in users.values()}


def fetch_following(cl: Client, user_id: str) -> set[str]:
    users = cl.user_following(user_id, amount=0)
    return {u.username for u in users.values()}


def get_user_id_by_username(cl: Client, username: str) -> str:
    user = cl.user_info_by_username(username)
    return str(user.pk)


def login() -> tuple[Client, str]:
    cl = _get_client()
    target = os.environ.get("TARGET_USERNAME", "jana_pirkova_")
    target_id = get_user_id_by_username(cl, target)
    return cl, target, target_id
