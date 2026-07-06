#!/usr/bin/env python3
"""
Instagram Monitor pro vice uctu.
Sleduje zmeny ve followers/following, Close Friends status,
nove stories, komentare pod prispevky a statistiky oznaceni/komentaru.

Spusteni:
    pip install instagrapi
    python monitor.py                # normalni monitoring
    python monitor.py --stats        # analyza kdo nejvic komentuje/je oznacovany
    python monitor.py --summary      # celkovy souhrn pres vsechny ucty
    python monitor.py --highlights   # vypis vsech stories z highlightu
"""

import json
import os
import re
import time
import getpass
import argparse
from collections import Counter
from datetime import datetime
from instagrapi import Client

TARGETS = ["jana_pirkova_", "pirkovis"]

MALE_NAMES = {
    "adam", "ales", "alexandr", "alfred", "andrej", "antonin", "boris",
    "dalibor", "dan", "daniel", "david", "denis", "dominik", "dušan",
    "erik", "filip", "frantisek", "honza", "hynek", "ivan", "ivo",
    "jakub", "jan", "jarda", "jarek", "jaromir", "jaroslav", "jiri",
    "jindrich", "josef", "karel", "kuba", "ladislav", "leos", "libor",
    "lubomir", "lubos", "ludek", "ludvik", "lukas", "marek", "marian",
    "mario", "martin", "matej", "matous", "matyáš", "max", "michal",
    "milan", "milos", "miroslav", "mojmir", "nikolas", "oldrich", "ondra",
    "ondrej", "otakar", "patrik", "pavel", "pepa", "petr", "premysl",
    "radek", "radim", "radovan", "richard", "robert", "robin", "roman",
    "rostislav", "samuel", "simon", "stanislav", "stepan", "tadeáš",
    "tomas", "vaclav", "viktor", "vilém", "vit", "vitek", "vladimir",
    "vladan", "vojtech", "zdenek", "alex", "tobias", "krystof",
    "sebastian", "nicolas", "noel", "oliver", "oskar", "theodor",
}

_gender_cache = {}


def is_male_user(cl, username):
    if username in _gender_cache:
        return _gender_cache[username]

    try:
        user_info = cl.user_info_by_username(username)
        full_name = (user_info.full_name or "").lower().strip()
        first_name = full_name.split()[0] if full_name else ""

        # remove diacritics for matching
        import unicodedata
        first_clean = "".join(
            c for c in unicodedata.normalize("NFD", first_name)
            if unicodedata.category(c) != "Mn"
        )

        is_male = first_clean in MALE_NAMES
        _gender_cache[username] = is_male
        return is_male
    except Exception:
        _gender_cache[username] = False
        return False


def guy_tag(cl, username):
    if is_male_user(cl, username):
        return " !!! KLUK !!!"
    return ""
CLOSE_FRIENDS_WATCH = ["jana_pirkova_", "pirkovis"]
STORIES_WATCH = ["jana_pirkova_", "pirkovis"]
COMMENTS_WATCH = ["jana_pirkova_", "pirkovis"]
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CREDS_FILE = os.path.join(DATA_DIR, "credentials.json")
SESSION_FILE = os.path.join(DATA_DIR, "session.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")
CF_STATUS_FILE = os.path.join(DATA_DIR, "close_friends_status.json")
SEEN_STORIES_FILE = os.path.join(DATA_DIR, "seen_stories.json")
SEEN_COMMENTS_FILE = os.path.join(DATA_DIR, "seen_comments.json")
CHECK_INTERVAL = 30
POSTS_TO_CHECK = 5


def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_credentials():
    ensure_dir()
    if os.path.exists(CREDS_FILE):
        with open(CREDS_FILE, encoding="utf-8") as f:
            return json.load(f)

    print("=== Prvni spusteni ===")
    print("Potrebuji tvuj Instagram login (pro pristup k API).")
    print()
    username = input("Instagram username: ").strip()
    password = getpass.getpass("Instagram heslo: ").strip()

    creds = {"username": username, "password": password}
    with open(CREDS_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f)
    os.chmod(CREDS_FILE, 0o600)
    print("Ulozeno.\n")
    return creds


def ig_login():
    creds = get_credentials()
    cl = Client()

    if os.path.exists(SESSION_FILE):
        cl.load_settings(SESSION_FILE)

    cl.login(creds["username"], creds["password"])
    ensure_dir()
    cl.dump_settings(SESSION_FILE)
    return cl


def fetch_users(cl, user_id, fetch_fn):
    users = fetch_fn(user_id, amount=0)
    return {u.username for u in users.values()}


def snapshot_file(target):
    return os.path.join(DATA_DIR, f"snapshot_{target}.json")


def load_snapshot(target):
    path = snapshot_file(target)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return set(data["followers"]), set(data["following"])


def save_snapshot(target, followers, following):
    ensure_dir()
    with open(snapshot_file(target), "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "followers": sorted(followers),
            "following": sorted(following),
        }, f, ensure_ascii=False, indent=2)


def load_cf_status():
    if not os.path.exists(CF_STATUS_FILE):
        return {}
    with open(CF_STATUS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_cf_status(status):
    ensure_dir()
    with open(CF_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def load_seen_stories():
    if not os.path.exists(SEEN_STORIES_FILE):
        return {}
    with open(SEEN_STORIES_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_seen_stories(seen):
    ensure_dir()
    with open(SEEN_STORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def load_seen_comments():
    if not os.path.exists(SEEN_COMMENTS_FILE):
        return {}
    with open(SEEN_COMMENTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_seen_comments(seen):
    ensure_dir()
    with open(SEEN_COMMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def fetch_highlight_items_raw(cl, highlight_pk):
    try:
        result = cl.private_request(
            "feed/reels_media/",
            data={"reel_ids": [f"highlight:{highlight_pk}"]},
        )
        reels = result.get("reels", {})
        reel = reels.get(f"highlight:{highlight_pk}", {})
        return reel.get("items", [])
    except Exception:
        result = cl.private_request(
            f"feed/reels_media/?reel_ids=highlight:{highlight_pk}"
        )
        reels = result.get("reels", {})
        reel = reels.get(f"highlight:{highlight_pk}", {})
        return reel.get("items", [])


def parse_raw_story(item):
    media_type = "video" if item.get("media_type") == 2 else "foto"
    taken_ts = item.get("taken_at", 0)
    taken = datetime.fromtimestamp(taken_ts).strftime("%d.%m.%Y %H:%M") if taken_ts else "?"

    details = []
    mentions = []

    reel_mentions = item.get("reel_mentions", [])
    for m in reel_mentions:
        user = m.get("user", {})
        username = user.get("username", "?")
        mentions.append(username)
        details.append(f"oznacen/a: @{username}")

    story_feed_media = item.get("story_feed_media", [])
    if story_feed_media:
        details.append("sdileny prispevek")

    story_hashtags = item.get("story_hashtags", [])
    for h in story_hashtags:
        hashtag = h.get("hashtag", {})
        name = hashtag.get("name", "")
        if name:
            details.append(f"#{name}")

    story_locations = item.get("story_locations", [])
    for loc in story_locations:
        location = loc.get("location", {})
        loc_name = location.get("name", "")
        if loc_name:
            details.append(f"lokace: {loc_name}")

    story_polls = item.get("story_polls", [])
    for p in story_polls:
        poll = p.get("poll_sticker", {})
        question = poll.get("question", "")
        if question:
            details.append(f"anketa: {question}")

    story_questions = item.get("story_questions", [])
    for q in story_questions:
        qs = q.get("question_sticker", {})
        question = qs.get("question", "")
        if question:
            details.append(f"otazka: {question}")

    story_quizs = item.get("story_quizs", [])
    for q in story_quizs:
        quiz = q.get("quiz_sticker", {})
        question = quiz.get("question", "")
        if question:
            details.append(f"kviz: {question}")

    story_sliders = item.get("story_sliders", [])
    if story_sliders:
        details.append("slider/emoji reakce")

    return media_type, taken, details, mentions


def log_event(text):
    ensure_dir()
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def ts():
    return datetime.now().strftime("%H:%M:%S")


def format_story_detail(s, target, cl=None):
    media_type = "video" if s.media_type == 2 else "foto"
    is_cf = getattr(s, "is_close_friends", False)
    cf_tag = " [CLOSE FRIENDS]" if is_cf else ""
    taken = s.taken_at.strftime("%d.%m. %H:%M") if s.taken_at else "?"

    details = []

    if hasattr(s, "mentions") and s.mentions:
        for m in s.mentions:
            tag = guy_tag(cl, m.user.username) if cl else ""
            details.append(f"oznacen/a: @{m.user.username}{tag}")

    if hasattr(s, "story_feed_media") and s.story_feed_media:
        details.append("sdileny prispevek")

    if hasattr(s, "story_hashtags") and s.story_hashtags:
        for h in s.story_hashtags:
            if hasattr(h, "hashtag") and h.hashtag:
                details.append(f"#{h.hashtag.name}")

    if hasattr(s, "story_locations") and s.story_locations:
        for loc in s.story_locations:
            if hasattr(loc, "location") and loc.location:
                details.append(f"lokace: {loc.location.name}")

    if hasattr(s, "story_stickers") and s.story_stickers:
        for st in s.story_stickers:
            if hasattr(st, "story_sticker_type"):
                details.append(f"sticker: {st.story_sticker_type}")

    if hasattr(s, "story_polls") and s.story_polls:
        for p in s.story_polls:
            if hasattr(p, "poll") and p.poll:
                details.append(f"anketa: {p.poll.question}")

    if hasattr(s, "story_questions") and s.story_questions:
        for q in s.story_questions:
            if hasattr(q, "question_sticker") and q.question_sticker:
                details.append(f"otazka: {q.question_sticker.question}")

    if hasattr(s, "story_sliders") and s.story_sliders:
        details.append("slider/emoji reakce")

    if hasattr(s, "story_quizs") and s.story_quizs:
        for q in s.story_quizs:
            if hasattr(q, "quiz") and q.quiz:
                details.append(f"kviz: {q.quiz.question}")

    detail_str = f" | {', '.join(details)}" if details else ""

    return f"@{target} {media_type} {taken}{cf_tag}{detail_str}", is_cf


def check_stories(cl, target, target_id):
    print(f"[{ts()}] Kontroluji stories @{target}...")

    try:
        stories = cl.user_stories(target_id)
    except Exception as e:
        print(f"[{ts()}] Nepodarilo se stahnout stories: {e}")
        return []

    if not stories:
        print(f"[{ts()}] @{target} nema zadne aktivni stories.")
        return []

    seen = load_seen_stories()
    seen_ids = set(seen.get(target, []))
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    new_stories = [s for s in stories if str(s.pk) not in seen_ids]
    cf_stories = [s for s in stories if getattr(s, "is_close_friends", False)]

    if cf_stories:
        print(f"[{ts()}] @{target} ma {len(cf_stories)} CLOSE FRIENDS stories:")
        for s in cf_stories:
            detail, _ = format_story_detail(s, target, cl)
            print(f"  [CF] {detail}")

    if new_stories:
        print(f"[{ts()}] @{target} ma {len(new_stories)} novych stories!")
        for s in new_stories:
            detail, is_cf = format_story_detail(s, target, cl)
            msg = f"[{now}]  STORY    {detail}"
            print(f"  >>> {msg}")
            log_event(msg)
    else:
        print(f"[{ts()}] @{target} ma {len(stories)} stories, zadne nove.")

    seen[target] = [str(s.pk) for s in stories]
    save_seen_stories(seen)

    return stories


def check_close_friends(stories, target):
    cf_stories = [s for s in stories if getattr(s, "is_close_friends", False)]
    has_cf = len(cf_stories) > 0
    total_stories = len(stories)

    cf_status = load_cf_status()
    old_status = cf_status.get(target)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    if total_stories == 0:
        pass
    elif has_cf:
        print(f"[{ts()}] VIDIS Close Friends story @{target}! Jsi ve vyberech.")
        if old_status == "not_in_cf":
            msg = f"[{now}]  !!!  @{target} te PRIDALA zpet do Close Friends!"
            print(f"  >>> {msg}")
            log_event(msg)
        cf_status[target] = "in_cf"
    else:
        print(f"[{ts()}] @{target} ma {total_stories} stories, ale zadne Close Friends.")
        if old_status == "in_cf":
            msg = f"[{now}]  !!!  @{target} te mozna ODSTRANILA z Close Friends! (ma stories ale zadne CF)"
            print(f"  >>> {msg}")
            log_event(msg)
        if old_status is None:
            cf_status[target] = "unknown"
        else:
            cf_status[target] = "not_in_cf"

    save_cf_status(cf_status)


def check_comments(cl, target, target_id):
    print(f"[{ts()}] Kontroluji komentare pod prispevky @{target}...")

    try:
        medias = cl.user_medias(int(target_id), amount=POSTS_TO_CHECK)
    except Exception as e:
        print(f"[{ts()}] Nepodarilo se stahnout prispevky: {e}")
        return

    if not medias:
        print(f"[{ts()}] @{target} nema zadne prispevky.")
        return

    seen = load_seen_comments()
    if target not in seen:
        seen[target] = {}

    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    total_new = 0

    for media in medias:
        media_pk = str(media.pk)
        seen_comment_ids = set(seen[target].get(media_pk, []))

        try:
            comments = cl.media_comments(media.pk, amount=20)
        except Exception as e:
            print(f"[{ts()}] Nepodarilo se stahnout komentare: {e}")
            continue

        new_comments = [c for c in comments if str(c.pk) not in seen_comment_ids]

        if not seen_comment_ids and new_comments:
            seen[target][media_pk] = [str(c.pk) for c in comments]
            if not seen.get(target + "_initialized"):
                continue

        for c in new_comments:
            text = c.text[:80] if c.text else ""
            author = c.user.username if c.user else "?"
            tag = guy_tag(cl, author) if author != "?" else ""
            msg = f"[{now}]  KOMENT   @{author} komentoval/a prispevek @{target}: \"{text}\"{tag}"
            print(f"  >>> {msg}")
            log_event(msg)
            total_new += 1

        seen[target][media_pk] = [str(c.pk) for c in comments]

    seen[target + "_initialized"] = True

    if total_new == 0:
        print(f"[{ts()}] Zadne nove komentare.")
    else:
        print(f"[{ts()}] Celkem {total_new} novych komentaru.")

    save_seen_comments(seen)


def check_target(cl, target, target_id):
    print(f"\n[{ts()}] --- @{target} ---")

    print(f"[{ts()}] Stahuji followers @{target}...")
    followers = fetch_users(cl, target_id, cl.user_followers)

    print(f"[{ts()}] Stahuji following @{target}...")
    following = fetch_users(cl, target_id, cl.user_following)

    print(f"[{ts()}] @{target} ma {len(followers)} sledujicich, sleduje {len(following)} lidi")

    previous = load_snapshot(target)

    if previous is None:
        print(f"[{ts()}] Prvni kontrola @{target} — ukladam snapshot. Zmeny uvidis priste.")
        save_snapshot(target, followers, following)
        return

    old_followers, old_following = previous
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    changes = False

    new_followers = followers - old_followers
    lost_followers = old_followers - followers
    new_following = following - old_following
    lost_following = old_following - following

    for u in sorted(new_followers):
        tag = guy_tag(cl, u)
        msg = f"[{now}]  +sledujici   @{u} zacal sledovat @{target}{tag}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    for u in sorted(lost_followers):
        tag = guy_tag(cl, u)
        msg = f"[{now}]  -sledujici   @{u} prestal sledovat @{target}{tag}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    for u in sorted(new_following):
        tag = guy_tag(cl, u)
        msg = f"[{now}]  +sleduje     @{target} zacal/a sledovat @{u}{tag}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    for u in sorted(lost_following):
        tag = guy_tag(cl, u)
        msg = f"[{now}]  -sleduje     @{target} prestal/a sledovat @{u}{tag}"
        print(f"  >>> {msg}")
        log_event(msg)
        changes = True

    if not changes:
        print(f"[{ts()}] Zadne zmeny.")

    save_snapshot(target, followers, following)


def run_stats(cl, targets):
    for target in targets:
        print(f"\n{'=' * 50}")
        print(f"  STATISTIKY @{target}")
        print(f"{'=' * 50}")

        try:
            info = cl.user_info_by_username(target)
            target_id = str(info.pk)
        except Exception as e:
            print(f"  CHYBA: {e}")
            continue

        mention_counter = Counter()
        comment_counter = Counter()
        tag_counter = Counter()

        # Analyzuj vsechny prispevky
        print(f"\n  Stahuji prispevky @{target}...")
        try:
            medias = cl.user_medias(int(target_id), amount=0)
        except Exception as e:
            print(f"  CHYBA pri stahovani prispevku: {e}")
            medias = []

        print(f"  Nalezeno {len(medias)} prispevku. Analyza...")

        for i, media in enumerate(medias):
            # Oznaceni v prispevku (tagy)
            if hasattr(media, "usertags") and media.usertags:
                for tag in media.usertags:
                    if hasattr(tag, "user") and tag.user:
                        tag_counter[tag.user.username] += 1

            # Zminky v caption
            if media.caption_text:
                caption_mentions = re.findall(r"@(\w+)", media.caption_text)
                for m in caption_mentions:
                    mention_counter[m] += 1

            # Komentare
            try:
                comments = cl.media_comments(media.pk, amount=0)
                for c in comments:
                    if c.user:
                        comment_counter[c.user.username] += 1
            except Exception:
                pass

            if (i + 1) % 10 == 0:
                print(f"  ... zpracovano {i + 1}/{len(medias)} prispevku")

        # Analyzuj stories (jen aktivni)
        print(f"\n  Kontroluji aktivni stories @{target}...")
        try:
            stories = cl.user_stories(target_id)
            for s in stories:
                if hasattr(s, "mentions") and s.mentions:
                    for m in s.mentions:
                        mention_counter[m.user.username] += 1
            print(f"  {len(stories)} aktivnich stories.")
        except Exception:
            pass

        # Analyzuj highlights (vybery)
        print(f"\n  Stahuji highlights (vybery) @{target}...")
        highlight_mention_counter = Counter()
        total_highlight_stories = 0
        try:
            highlights = cl.user_highlights(int(target_id))
            print(f"  Nalezeno {len(highlights)} highlightu.")
            for hl in highlights:
                try:
                    items = fetch_highlight_items_raw(cl, hl.pk)
                    total_highlight_stories += len(items)
                    for item in items:
                        _, _, _, item_mentions = parse_raw_story(item)
                        for username in item_mentions:
                            highlight_mention_counter[username] += 1
                            mention_counter[username] += 1
                except Exception:
                    pass
            print(f"  Celkem {total_highlight_stories} stories ve vyberech.")
        except Exception as e:
            print(f"  CHYBA pri stahovani highlightu: {e}")

        # Vysledky
        print(f"\n  --- Nejvice oznacovani v postech (tagy na fotkach) ---")
        if tag_counter:
            for user, count in tag_counter.most_common(15):
                tag = guy_tag(cl, user)
                print(f"    {count:>4}x  @{user}{tag}")
        else:
            print(f"    Zadne tagy.")

        print(f"\n  --- Nejvice zminovani v popisech (@zminky) ---")
        if mention_counter:
            for user, count in mention_counter.most_common(15):
                tag = guy_tag(cl, user)
                print(f"    {count:>4}x  @{user}{tag}")
        else:
            print(f"    Zadne zminky.")

        print(f"\n  --- Nejvice komentujici ---")
        if comment_counter:
            for user, count in comment_counter.most_common(15):
                tag = guy_tag(cl, user)
                print(f"    {count:>4}x  @{user}{tag}")
        else:
            print(f"    Zadne komentare.")

        print(f"\n  --- Nejvice oznacovani ve vyberech (highlights) ---")
        if highlight_mention_counter:
            for user, count in highlight_mention_counter.most_common(15):
                tag = guy_tag(cl, user)
                print(f"    {count:>4}x  @{user}{tag}")
        else:
            print(f"    Zadne oznaceni ve vyberech.")

        total_tags = sum(tag_counter.values())
        total_mentions = sum(mention_counter.values())
        total_comments = sum(comment_counter.values())
        print(f"\n  CELKEM: {len(medias)} prispevku, {total_highlight_stories} stories ve vyberech, {total_tags} tagu, {total_mentions} zminek, {total_comments} komentaru")


def run_highlights(cl, targets):
    for target in targets:
        print(f"\n{'=' * 50}")
        print(f"  VYBERY (HIGHLIGHTS) @{target}")
        print(f"{'=' * 50}")

        try:
            info = cl.user_info_by_username(target)
            target_id = str(info.pk)
        except Exception as e:
            print(f"  CHYBA: {e}")
            continue

        try:
            highlights = cl.user_highlights(int(target_id))
        except Exception as e:
            print(f"  CHYBA pri stahovani highlightu: {e}")
            continue

        if not highlights:
            print(f"  @{target} nema zadne vybery.")
            continue

        print(f"  Nalezeno {len(highlights)} vyberu.\n")

        for hl in highlights:
            hl_title = hl.title or "(bez nazvu)"
            print(f"  --- Vyber: {hl_title} ---")

            try:
                items = fetch_highlight_items_raw(cl, hl.pk)
            except Exception as e:
                print(f"    CHYBA: {e}")
                continue

            if not items:
                print(f"    Prazdny vyber.")
                continue

            print(f"    {len(items)} stories:\n")

            for item in items:
                media_type, taken, details, mentions = parse_raw_story(item)
                tagged_details = []
                for d in details:
                    if d.startswith("oznacen/a: @"):
                        uname = d.split("@", 1)[1]
                        tag = guy_tag(cl, uname)
                        tagged_details.append(f"{d}{tag}")
                    else:
                        tagged_details.append(d)
                detail_str = f"\n             {', '.join(tagged_details)}" if tagged_details else ""
                print(f"    [{taken}] {media_type}{detail_str}")

            print()


def run_summary(cl, targets):
    print(f"\n{'=' * 60}")
    print(f"  SOUHRNNE STATISTIKY — {', '.join('@' + t for t in targets)}")
    print(f"{'=' * 60}")

    total_tag = Counter()
    total_mention = Counter()
    total_comment = Counter()
    total_highlight_mention = Counter()
    total_posts = 0
    total_hl_stories = 0

    for target in targets:
        print(f"\n  Zpracovavam @{target}...")

        try:
            info = cl.user_info_by_username(target)
            target_id = str(info.pk)
        except Exception as e:
            print(f"  CHYBA: {e}")
            continue

        try:
            medias = cl.user_medias(int(target_id), amount=0)
        except Exception:
            medias = []

        total_posts += len(medias)

        for i, media in enumerate(medias):
            if hasattr(media, "usertags") and media.usertags:
                for tag in media.usertags:
                    if hasattr(tag, "user") and tag.user:
                        total_tag[tag.user.username] += 1

            if media.caption_text:
                for m in re.findall(r"@(\w+)", media.caption_text):
                    total_mention[m] += 1

            try:
                comments = cl.media_comments(media.pk, amount=0)
                for c in comments:
                    if c.user:
                        total_comment[c.user.username] += 1
            except Exception:
                pass

            if (i + 1) % 10 == 0:
                print(f"    ... {i + 1}/{len(medias)} prispevku @{target}")

        try:
            stories = cl.user_stories(target_id)
            for s in stories:
                if hasattr(s, "mentions") and s.mentions:
                    for m in s.mentions:
                        total_mention[m.user.username] += 1
        except Exception:
            pass

        try:
            highlights = cl.user_highlights(int(target_id))
            for hl in highlights:
                try:
                    items = fetch_highlight_items_raw(cl, hl.pk)
                    total_hl_stories += len(items)
                    for item in items:
                        _, _, _, item_mentions = parse_raw_story(item)
                        for username in item_mentions:
                            total_highlight_mention[username] += 1
                            total_mention[username] += 1
                except Exception:
                    pass
        except Exception:
            pass

    print(f"\n{'=' * 60}")
    print(f"  CELKOVE VYSLEDKY ({', '.join('@' + t for t in targets)})")
    print(f"  {total_posts} prispevku, {total_hl_stories} stories ve vyberech")
    print(f"{'=' * 60}")

    print(f"\n  --- Nejvice oznacovani v postech (tagy na fotkach) ---")
    if total_tag:
        for user, count in total_tag.most_common(15):
            tag = guy_tag(cl, user)
            print(f"    {count:>4}x  @{user}{tag}")
    else:
        print(f"    Zadne tagy.")

    print(f"\n  --- Nejvice zminovani celkem (@zminky + highlights) ---")
    if total_mention:
        for user, count in total_mention.most_common(15):
            tag = guy_tag(cl, user)
            print(f"    {count:>4}x  @{user}{tag}")
    else:
        print(f"    Zadne zminky.")

    print(f"\n  --- Nejvice komentujici ---")
    if total_comment:
        for user, count in total_comment.most_common(15):
            tag = guy_tag(cl, user)
            print(f"    {count:>4}x  @{user}{tag}")
    else:
        print(f"    Zadne komentare.")

    print(f"\n  --- Nejvice oznacovani ve vyberech (highlights) ---")
    if total_highlight_mention:
        for user, count in total_highlight_mention.most_common(15):
            tag = guy_tag(cl, user)
            print(f"    {count:>4}x  @{user}{tag}")
    else:
        print(f"    Zadne oznaceni ve vyberech.")

    combined = total_tag + total_mention + total_comment + total_highlight_mention
    print(f"\n  --- TOP 15 celkove (tagy + zminky + komentare + highlights) ---")
    if combined:
        for user, count in combined.most_common(15):
            tag = guy_tag(cl, user)
            print(f"    {count:>4}x  @{user}{tag}")

    print()


def check():
    print(f"[{ts()}] Prihlasuji se...")
    cl = ig_login()

    all_targets = set(TARGETS + STORIES_WATCH + CLOSE_FRIENDS_WATCH + COMMENTS_WATCH)
    target_ids = {}
    for target in all_targets:
        try:
            info = cl.user_info_by_username(target)
            target_ids[target] = str(info.pk)
        except Exception as e:
            print(f"[{ts()}] CHYBA pri hledani @{target}: {e}")

    for target in TARGETS:
        if target not in target_ids:
            continue
        try:
            check_target(cl, target, target_ids[target])
        except Exception as e:
            print(f"[{ts()}] CHYBA u @{target}: {e}")

    for target in STORIES_WATCH:
        if target not in target_ids:
            continue
        try:
            stories = check_stories(cl, target, target_ids[target])
            if target in CLOSE_FRIENDS_WATCH:
                check_close_friends(stories, target)
        except Exception as e:
            print(f"[{ts()}] CHYBA stories @{target}: {e}")

    for target in COMMENTS_WATCH:
        if target not in target_ids:
            continue
        try:
            check_comments(cl, target, target_ids[target])
        except Exception as e:
            print(f"[{ts()}] CHYBA komentare @{target}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Instagram Monitor")
    parser.add_argument("--stats", action="store_true",
                        help="Analyza: kdo nejvic komentuje a je oznacovany")
    parser.add_argument("--highlights", action="store_true",
                        help="Vypis vsech stories ze vsech vyberu (highlights)")
    parser.add_argument("--summary", action="store_true",
                        help="Celkovy souhrn pres vsechny ucty dohromady")
    parser.add_argument("--stats-target", nargs="*",
                        help="Ucty pro analyzu (vychozi: jana_pirkova_ pirkovis)")
    args = parser.parse_args()

    if args.summary:
        print("Prihlasuji se...")
        cl = ig_login()
        targets = args.stats_target if args.stats_target else ["jana_pirkova_", "pirkovis"]
        run_summary(cl, targets)
        return

    if args.highlights:
        print("Prihlasuji se...")
        cl = ig_login()
        targets = args.stats_target if args.stats_target else ["jana_pirkova_", "pirkovis"]
        run_highlights(cl, targets)
        return

    if args.stats:
        print("Prihlasuji se...")
        cl = ig_login()
        targets = args.stats_target if args.stats_target else ["jana_pirkova_", "pirkovis"]
        run_stats(cl, targets)
        return

    print(f"{'=' * 50}")
    print(f"  Instagram Monitor")
    print(f"  Sleduji: {', '.join('@' + t for t in TARGETS)}")
    print(f"  Stories: {', '.join('@' + t for t in STORIES_WATCH)}")
    print(f"  Komentare: {', '.join('@' + t for t in COMMENTS_WATCH)}")
    print(f"  Close Friends: {', '.join('@' + t for t in CLOSE_FRIENDS_WATCH)}")
    print(f"  Kontrola kazdych {CHECK_INTERVAL} minut")
    print(f"  Ctrl+C pro ukonceni")
    print(f"{'=' * 50}")
    print()

    while True:
        try:
            check()
        except KeyboardInterrupt:
            print("\nUkonceno.")
            break
        except Exception as e:
            print(f"[{ts()}] CHYBA: {e}")

        print(f"\n[{ts()}] Dalsi kontrola za {CHECK_INTERVAL} min...\n")
        try:
            time.sleep(CHECK_INTERVAL * 60)
        except KeyboardInterrupt:
            print("\nUkonceno.")
            break


if __name__ == "__main__":
    main()
