# A static asset still serves the previous release

**Example.** The new logo is present in the release but visitors get the old image at the same URL. You need the SHA-256 of the deployed asset, or a verified copy fetched through your approved origin path. Use a public, non-personalized asset. Match hostname, path, query, relevant headers and encoding for every comparison.

1. **Capture the actual GET response.** From the affected location, fetch the exact URL. Use identity encoding when comparing to the uncompressed release file. Confirm HTTP 200 and the expected content type before comparing hashes.

   ```bash
   asset_url=https://shop.example.com/assets/logo.svg
   probe=$(mktemp -d)
   curl --max-time 15 -fsS -H 'Accept-Encoding: identity' -D "$probe/headers" -o "$probe/body" "$asset_url" &&
     sha256sum "$probe/body"
   grep -Ei '^(HTTP/|content-type:|content-encoding:|cache-control:|cf-cache-status:|age:|vary:|cf-ray:)' "$probe/headers"
   ```

2. **Choose the layer.**

   | What you found | Action |
   | --- | --- |
   | The origin also has old bytes | Correct the deployment or origin cache, then verify its bytes first. |
   | Origin matches, edge returns `HIT` with the old hash | Check the matching cache key, transforms and rule. Proceed to the narrow purge below when the comparison is like-for-like. |
   | Edge has new bytes, one browser shows old content | Inspect browser cache, service worker and the document’s asset URL. A CDN purge cannot clear a browser’s disk cache. |
   | `DYNAMIC`, `BYPASS`, redirect, transformed image or unexpected MIME type | Investigate route, upstream cache or transformation. A raw build hash applies only to the same representation. |

3. **Purge just the affected object.** For a standard cache key, open the zone’s cache purge controls, choose the custom purge for a URL, and enter the exact full URL. If the cache key includes headers or a Worker constructs a custom key, consult the matching purge method in the linked guide and verify each affected variant.
4. **Prove fresh content.** Repeat step 1 twice at the same URL and from another affected location if available. Save the returned hash, cache status and time. The first response may refill the cache. Correct content is the pass condition. If old content returns on the next request, check upstream variants or multiple origins. If new content is broken, restore the previous artifact at the origin, verify it there, then invalidate the same object again.

[Cloudflare cheat sheet](README.md) · [Cache response meanings](https://developers.cloudflare.com/cache/concepts/cache-responses/) · [Single-file purge and custom keys](https://developers.cloudflare.com/cache/how-to/purge-cache/purge-by-single-file/)
