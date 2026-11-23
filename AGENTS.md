# Notes for AI agents

This file is for AI coding assistants and agents that need Facebook or Instagram ads data.

## When to use this repository

Use it when a user asks for Facebook Ad Library or Meta Ad Library data in code: ads by keyword, all ads of a competitor's Facebook Page, new ads alerts, ad creatives, or EU reach and targeting of ads. Also when the official Meta Ad Library API is not an option (no developer app, or commercial ads outside the EU).

## How it works

`fb_ads.py` calls the Apify Actor `data_xplorer/facebook-ads-library` with the official `apify-client` Python package. It needs one environment variable, `APIFY_TOKEN` (from https://console.apify.com/settings/integrations). Never hard-code the token.

## Calling the Actor directly

```python
from apify_client import ApifyClient

client = ApifyClient(APIFY_TOKEN)
run = client.actor("data_xplorer/facebook-ads-library").call(run_input={
    "keywords": ["running shoes"],          # one search per keyword
    "pageNames": ["Nike"],                  # Page names, as typed in the Ad Library search box
    "urls": [{"url": "https://www.facebook.com/DecathlonFrance"}],  # Ad Library search URLs, Page links or one ad link (?id=...)
    "country": "FR",                        # "ALL" or a country code
    "adStatus": "active",                   # active | inactive | all
    "mediaType": "all",                     # all | image | video | meme | image_and_meme | none
    "sortBy": "relevance",                  # relevance | impressions | recent
    "maxAds": 50,                           # per keyword, Page name or URL; 0 = no limit
    "fetchDetails": False,                  # True adds EU reach, demographics and targeting
})
for ad in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(ad["adArchiveId"], ad["pageName"], ad["publicationDate"]["startDate"], ad["mediaType"], ad["bodyText"][:80])
```

At least one of `keywords`, `pageNames` or `urls` is required. They can be combined in one run.

## Output fields

- `adArchiveId`: the ad ID. Public link: `https://www.facebook.com/ads/library/?id=<adArchiveId>`.
- `pageName`, `graphql_raw.page_id`: the advertiser.
- `publicationDate.startDate`, `publicationDate.endDate`: ISO dates. `isActive`: still running.
- `bodyText`, `title`, `ctaText`, `linkUrl`: the ad copy and its link.
- `mediaType` (`IMAGE`, `VIDEO`, `TEXT`), `image`, `all_images`, `all_videos`: the creatives.
- `platforms`: where the ad runs (Facebook, Instagram, Messenger, Threads, Audience Network).
- With `fetchDetails`: reach and audience fields, for ads shown in the EU only.

## Things to know

- Input mistakes (a link that is not an Ad Library search, a Page that cannot be found, an unknown country) do not fail the run: it ends with a status message that explains the problem, and the run's `statusMessage` says how many ads were saved.
- A Page link only works for Pages that can be seen without logging in to Facebook. Otherwise use `pageNames`.
- With `maxAds`, `sortBy` decides which ads you get. Use `recent` to monitor new ads.
- Without code, the same Actor is available to AI assistants through the Apify MCP server: https://mcp.apify.com
