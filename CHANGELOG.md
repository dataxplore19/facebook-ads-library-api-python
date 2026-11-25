# Changelog

Updates to the [Facebook Ads Library](https://apify.com/data_xplorer/facebook-ads-library?fpr=6vi1cs) Actor used by this repository. Click **Watch > Custom > Releases** at the top of the page to be notified of new ones.

## Actor v1.6 (2026-11-25)

- More reliable connection: when the connection fails in the searched country, the Actor switches to another region and keeps it for the rest of the run. Results are the same.
- Short outages no longer end the run at once: the Actor waits a little and tries again before giving up, and stops cleanly if the connection stays down.

## Actor v1.5 (2026-11-22)

- Search by Page name: type `Nike` or `Decathlon France` and get that Page's ads, with the usual filters. Used by `python fb_ads.py page Nike`.
- Paste a Facebook Page link (`facebook.com/nike`) to get that Page's ads.
- Paste the link of one ad (`facebook.com/ads/library/?id=...`) to get that ad.
- More reliable searches: answers that contain ads are no longer mistaken for a Meta limit, and each session keeps the same connection from start to end.
- Clearer input checks: a link that is not an Ad Library search, an unknown country or a wrong date is explained in the run status instead of failing the run.

## Actor v1.4 (2026-11-20)

- Fewer empty results: when Facebook answers a search with an empty list although the Page has ads, the request is asked again before the run reports 0 ads.

## Actor v1.3 (2026-11-20)

- Clearer failure messages: a failed run says whether Meta limited the requests, the Ad Library could not be reached, or an unexpected error occurred.

## Actor v1.1 (2026-11-13)

- Search by keyword with filters (country, ad category, status, media type, platforms, language, dates, sort order, exact phrase), no Ad Library URL needed.
