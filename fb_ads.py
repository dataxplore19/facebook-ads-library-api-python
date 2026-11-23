"""Facebook Ad Library data in Python: ads by keyword, all ads of a Page, and alerts on new competitor ads.

Gets the data through the Apify Actor data_xplorer/facebook-ads-library, so there is no Meta access
token, no app review and no login to manage. Works for every country and every ad category, not only
political ads.

Examples:
    python fb_ads.py search "running shoes" --country US --max 50
    python fb_ads.py page Nike "Decathlon France" --country FR
    python fb_ads.py page https://www.facebook.com/nike --details
    python fb_ads.py watch Nike Adidas --country FR
"""
import argparse
import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from apify_client import ApifyClient

ACTOR = "data_xplorer/facebook-ads-library"
FIELDS = ["adArchiveId", "pageName", "pageId", "isActive", "startDate", "endDate", "mediaType", "platforms",
          "ctaText", "linkUrl", "title", "bodyText", "images", "videos", "adLibraryUrl"]


def run_actor(run_input):
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    run = client.actor(ACTOR).call(run_input=run_input, logger=None)
    if run.get("statusMessage"):
        print(run["statusMessage"])
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def base_input(args):
    return {
        "country": args.country,
        "adStatus": args.status,
        "mediaType": args.media,
        "maxAds": args.max,
        "fetchDetails": args.details,
    }


def flat(ad):
    """One CSV row per ad, with the ad's public Ad Library link."""
    dates = ad.get("publicationDate") or {}
    images = [ad.get("image"), *(ad.get("all_images") or [])]
    row = {
        "adArchiveId": ad.get("adArchiveId"),
        "pageName": ad.get("pageName"),
        "pageId": (ad.get("graphql_raw") or {}).get("page_id"),
        "isActive": ad.get("isActive"),
        "startDate": (dates.get("startDate") or "")[:10],
        "endDate": (dates.get("endDate") or "")[:10],
        "mediaType": ad.get("mediaType"),
        "platforms": " ".join(ad.get("platforms") or []),
        "ctaText": ad.get("ctaText"),
        "linkUrl": ad.get("linkUrl"),
        "title": ad.get("title"),
        "bodyText": ad.get("bodyText"),
        "images": " ".join(dict.fromkeys(i for i in images if i)),
        "videos": " ".join(ad.get("all_videos") or []),
        "adLibraryUrl": f"https://www.facebook.com/ads/library/?id={ad.get('adArchiveId')}",
    }
    return {k: "" if v is None else str(v).replace("\n", " ") for k, v in row.items()}


def write_csv(path, ads, extra=None):
    rows = [{**flat(ad), **(extra or {})} for ad in ads]
    header = FIELDS + list((extra or {}).keys())
    with Path(path).open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} ads written to {path}")


def notify(text):
    """Telegram message if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set, console otherwise."""
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print(text)
        return
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                  json={"chat_id": chat, "text": text, "disable_web_page_preview": True}, timeout=30)


def summary(ads):
    pages = {}
    for ad in ads:
        pages[ad.get("pageName") or "?"] = pages.get(ad.get("pageName") or "?", 0) + 1
    for name, n in sorted(pages.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {n:>4}  {name}")


def search(args):
    """Ads that match keywords, one search per keyword."""
    ads = run_actor({**base_input(args), "keywords": args.keywords, "exactPhrase": args.exact})
    print(f"{len(ads)} ads. Top advertisers:")
    summary(ads)
    write_csv(args.out, ads)


def page_input(args, pages):
    urls = [{"url": p} for p in pages if p.startswith("http")]
    names = [p for p in pages if not p.startswith("http")]
    return {**base_input(args), "urls": urls, "pageNames": names}


def page(args):
    """All ads of one or more Facebook Pages, from their name or their link."""
    ads = run_actor(page_input(args, args.pages))
    print(f"{len(ads)} ads.")
    summary(ads)
    write_csv(args.out, ads)


def watch(args):
    """Alert on ads that were not there in earlier runs, for each watched Page."""
    history = Path(args.out)
    first_run = not history.exists()
    seen = set()
    if not first_run:
        with history.open() as fh:
            seen = {row["adArchiveId"] for row in csv.DictReader(fh)}

    # Newest ads first, so a limit of N ads always covers the latest launches.
    ads = run_actor({**page_input(args, args.pages), "sortBy": "recent"})
    new = [ad for ad in ads if str(ad.get("adArchiveId")) not in seen]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    if not first_run:
        for ad in new[:args.alert_max]:
            text = (ad.get("bodyText") or ad.get("title") or "").replace("\n", " ")[:200]
            notify(f"New Facebook ad from {ad.get('pageName')} ({ad.get('mediaType')}, since {flat(ad)['startDate']}):\n"
                   f"{text}\nhttps://www.facebook.com/ads/library/?id={ad.get('adArchiveId')}")
        if len(new) > args.alert_max:
            notify(f"... and {len(new) - args.alert_max} more new ads. See {history}.")
        print(f"{len(ads)} ads checked, {len(new)} new.")
    else:
        print(f"First run: {len(ads)} ads saved as the starting point. Next runs alert on new ones.")

    with history.open("a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["firstSeenAt"] + FIELDS)
        if first_run:
            writer.writeheader()
        for ad in new:
            writer.writerow({"firstSeenAt": now, **flat(ad)})


def main():
    parser = argparse.ArgumentParser(description="Facebook Ad Library data in Python, via Apify.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p, out, max_ads):
        p.add_argument("--country", default="ALL", help="country code (US, FR, GB...), ALL for every country")
        p.add_argument("--status", default="active", choices=["active", "inactive", "all"])
        p.add_argument("--media", default="all", choices=["all", "image", "video", "meme", "none"])
        p.add_argument("--max", type=int, default=max_ads, help="max ads per keyword or Page (0 = no limit)")
        p.add_argument("--details", action="store_true", help="add EU reach, age, gender and targeting per ad")
        p.add_argument("--out", default=out)

    p = sub.add_parser("search", help="ads that match one or more keywords")
    p.add_argument("keywords", nargs="+")
    p.add_argument("--exact", action="store_true", help="match the keyword as an exact phrase")
    common(p, "ads.csv", 100)
    p.set_defaults(func=search)

    p = sub.add_parser("page", help="all ads of Facebook Pages, by name or link")
    p.add_argument("pages", nargs="+", help='Page names ("Nike") or links (https://www.facebook.com/nike)')
    common(p, "ads.csv", 100)
    p.set_defaults(func=page)

    p = sub.add_parser("watch", help="alert on new ads of competitor Pages")
    p.add_argument("pages", nargs="+", help='Page names ("Nike") or links (https://www.facebook.com/nike)')
    p.add_argument("--alert-max", type=int, default=5, help="max alert messages per run")
    common(p, "ads_history.csv", 200)
    p.set_defaults(func=watch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
