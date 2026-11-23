# Facebook Ads Library API for Python (Meta Ad Library)

Get Facebook and Instagram ads from the Meta Ad Library in Python: search ads by keyword, get every ad of a Facebook Page from its name or its link, and get a Telegram alert when a competitor launches a new ad. Results go to CSV.

The official Meta Ad Library API needs a Meta developer app, an identity check and an access token, and outside the EU it only returns political and issue ads. This script gets the data through the [Facebook Ads Library](https://apify.com/data_xplorer/facebook-ads-library?fpr=6vi1cs) Actor on Apify instead: every ad category, every country, no Meta account and no login.

> Click **Watch > Custom > Releases** at the top of this page to be notified when the Actor gets new features. See the [changelog](CHANGELOG.md).

## Video

[![Facebook Ads Library Scraper](https://img.youtube.com/vi/oCJ22eISa6E/maxresdefault.jpg)](https://www.youtube.com/watch?v=oCJ22eISa6E)

*Video: how the Facebook Ads Library Actor works.*

## What you can do

| Task | Command | Output |
| --- | --- | --- |
| Ads that match a keyword | `python fb_ads.py search "running shoes" --country US` | `ads.csv` |
| All ads of a Page, from its name | `python fb_ads.py page Nike --country FR` | `ads.csv` |
| All ads of a Page, from its link | `python fb_ads.py page https://www.facebook.com/nike` | `ads.csv` |
| Alert when a competitor launches a new ad | `python fb_ads.py watch Nike Adidas --country FR` | Telegram message |

## Quick start

You need Python 3.9+ and an [Apify](https://apify.com?fpr=6vi1cs) account (the free plan includes monthly credits).

```bash
git clone https://github.com/dataxplore19/facebook-ads-library-api-python.git
cd facebook-ads-library-api-python
pip install -r requirements.txt
export APIFY_TOKEN="your_apify_token"
python fb_ads.py search "running shoes" --country US --max 50
```

Telegram alerts are optional. Without these two variables, alerts are printed to the console.

```bash
export TELEGRAM_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

## Search ads by keyword

```bash
python fb_ads.py search "running shoes" --country US --max 10
```

```
10 ads saved from 1 keyword
10 ads. Top advertisers:
     4  KURU Footwear
     2  SHEIN
     1  HOKA
     1  On
10 ads written to ads.csv
```

`ads.csv` has one row per ad:

```csv
adArchiveId,pageName,pageId,isActive,startDate,endDate,mediaType,platforms,ctaText,linkUrl,title,bodyText,images,videos,adLibraryUrl
1339489931715040,KURU Footwear,71740214065,True,2026-07-06,2026-11-23,VIDEO,Facebook Instagram Audience Network,Shop now,https://www.kurufootwear.com/...,Get Comfort in the Chaos,"You saw the apocalypse...",https://scontent...,https://video...,https://www.facebook.com/ads/library/?id=1339489931715040
```

Several keywords in one command run one search each: `python fb_ads.py search nike adidas puma`. Add `--exact` to match the keyword as an exact phrase.

## Get all ads of a Facebook Page

By Page name, as you would type it in the Ad Library search box:

```bash
python fb_ads.py page Nike "Decathlon France" --country FR
```

Or by Page link:

```bash
python fb_ads.py page https://www.facebook.com/nike https://www.facebook.com/DecathlonFrance
```

The Actor finds the Page in the Ad Library, then returns its ads with the filters you set.

## Get an alert when a competitor launches a new ad

```bash
python fb_ads.py watch https://www.facebook.com/DecathlonFrance --country FR
```

The first run saves the Page's current ads in `ads_history.csv`. Every later run sends one message per new ad:

```
New Facebook ad from Decathlon France (IMAGE, since 2026-06-05):
Pour repousser vos limites, choisissez nos produits running Decathlon
https://www.facebook.com/ads/library/?id=1814474186198425
```

`watch` asks for the newest ads first, so `--max 200` (the default) covers the latest launches even on big advertisers. `--alert-max` caps the number of messages per run (5 by default).

Run it every morning with cron:

```bash
0 8 * * * cd /path/to/facebook-ads-library-api-python && APIFY_TOKEN=your_apify_token /usr/bin/python3 fb_ads.py watch Nike Adidas --country FR
```

## Options

Same options for `search`, `page` and `watch`:

- `--country`: country code where the ads were shown (`US`, `GB`, `FR`, `DE`...), `ALL` (default) for every country.
- `--status`: `active` (default), `inactive` or `all`.
- `--media`: `all` (default), `image`, `video`, `meme` or `none`.
- `--max`: maximum number of ads per keyword or Page. `0` means no limit.
- `--details`: adds EU reach, age and gender breakdown and targeting for each ad (for ads shown in the EU). Slower.
- `--out`: CSV file name.

## Use the data in pandas

```python
import pandas as pd

df = pd.read_csv("ads.csv", parse_dates=["startDate"])
df["days_running"] = (pd.Timestamp.today() - df["startDate"]).dt.days
print(df.sort_values("days_running", ascending=False)[["pageName", "title", "days_running"]].head(10))
```

Ads that have been running for a long time are usually the ones that work for the advertiser.

## FAQ

### Is there an official Facebook Ads Library API?

Yes, the Meta Ad Library API. It needs a Meta developer account, an identity confirmation and an access token. Outside the EU it only returns ads about social issues, elections or politics. Commercial ads shown in the US, for example, are not available through it.

### Can I get the ads of any Facebook Page?

Yes, any Page that runs ads, by name or by link. Pages that cannot be seen without logging in to Facebook cannot be found from their link: search them by name instead.

### Can I get the reach and audience of an ad?

For ads shown in the EU, yes: add `--details` to get the reach, the age and gender breakdown and the targeting. Meta only publishes these numbers for the EU.

### Does it get Instagram ads too?

Yes. The Ad Library covers Facebook, Instagram, Messenger, Threads and the Audience Network. The `platforms` column says where each ad runs.

### Can I use it from n8n, Make or another language?

Yes. The Actor is a plain HTTP API. See the [API tab of the Actor](https://apify.com/data_xplorer/facebook-ads-library/api?fpr=6vi1cs) for JavaScript, cURL and other examples.

### Can an AI agent use it?

Yes. See [AGENTS.md](AGENTS.md). The Actor is also available to AI assistants through the [Apify MCP server](https://mcp.apify.com).

## Disclosure

I am the author of the Facebook Ads Library Actor used by this script. Links to apify.com in this repository are referral links: if you create an Apify account through them, I may earn a commission at no cost to you.

## License

MIT
