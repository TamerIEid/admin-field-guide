# Cloudflare daily cheat sheet

For an administrator of a Cloudflare DNS zone and its web origin. Keep a known public test URL, expected content marker and an approved way to check origin health. Use a harmless anonymous GET. Save UTC time and Ray ID when a request fails.

| Question | First check | What the result means |
| --- | --- | --- |
| Which nameservers are delegated? | `dig +trace example.com NS` | Inspect the parent referral and compare with the zone’s assigned nameservers. A timeout may reflect local network policy. |
| Do resolvers agree? | `dig @1.1.1.1 www.example.com A +noall +answer +comments` and repeat with `@8.8.8.8` | Compare status, answer and remaining TTL. A proxied name normally returns Cloudflare addresses. |
| Does IPv6 follow the same path? | Repeat with `AAAA`, then compare `curl -4` and `curl -6` from a dual-stack client | An IPv6-only failure can be a stale AAAA record or client connectivity. Check the zone and a second client. |
| Did the edge serve cached bytes? | `curl -sS --max-time 12 -D - -o /dev/null https://www.example.com/logo.svg` | Read status, `CF-Cache-Status`, `Age` and `CF-Ray` together. `DYNAMIC` and `BYPASS` point toward eligibility or policy. |
| Has an edge or origin rule changed? | Zone’s DNS, cache rules, redirect rules, SSL/TLS mode and account audit logs where available | Match rule, hostname, edit time and actor to the failing request. |
| Where did a request fail? | Capture exact code, time, URL path and Ray ID, then compare origin logs | 522 points toward origin connectivity, 525 toward handshake failure, and 526 toward origin certificate validation. |
| Could the change affect mail? | `dig example.com MX +noall +answer`, then inspect proxy status of each mail host | Standard SMTP mail hosts generally require DNS-only addresses. Preserve their records when moving a web host. |

[Move one DNS record](dns-change.md) · [Stale cached asset](stale-asset.md) · [Origin errors](origin-errors.md) · [Proxy status](https://developers.cloudflare.com/dns/proxy-status/) · [Cache response headers](https://developers.cloudflare.com/cache/concepts/cache-responses/)
