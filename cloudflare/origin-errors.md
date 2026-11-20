# Trace a Cloudflare 522, 525 or 526

**You need** a failing hostname, an exact URL and UTC time, the origin configured for that route, and access to the origin owner. Use status and Ray ID from a fresh response. A shared 5xx screenshot alone cannot identify the failing layer.

1. **Confirm scope.** Fetch one failing route and a known healthy route with a short timeout. Record whether responses are cached and whether failures occur at multiple edge locations. A cached home page can stay healthy while the origin is unreachable.

   ```bash
   host=shop.example.com
   curl --max-time 25 -sS -D - -o /dev/null "https://$host/health"
   ```

   The sample timeout may expire before the edge returns an error page. When reproducing an observed 522, repeat with a timeout covering the observed incident latency or use the recorded failed request.
2. **Follow the exact code.**

   | Edge code | Origin-side checks | Next owner/action |
   | --- | --- | --- |
   | 522 connection timed out | Confirm saved origin address, listener, host load and recent firewall or rate-limit changes. Check whether the request reached the expected node. | Network/origin owner compares allow rules with current Cloudflare IP ranges and validates return routing and capacity. |
   | 525 TLS handshake failed | Match the failing time with TLS logs, correct SNI/vhost, port and configured protocols. Check recent certificate or listener deployment. | TLS owner repairs the failed negotiation on the affected origin. |
   | 526 invalid origin certificate | Under Full (strict), compare the certificate name, lifetime, issuer and served chain with what Cloudflare trusts. Check every target behind the hostname. | Certificate owner deploys the complete valid chain for the correct name. |

3. **Inspect one origin certificate where direct access is approved.** Set `origin` privately. The hostname supplies SNI and hostname verification. Use `-CAfile /path/to/approved-ca.pem` when this origin uses Cloudflare Origin CA or another applicable private trust chain. Client-certificate-protected origins require their normal trusted probe.

   ```bash
   origin=192.0.2.40
   timeout 12 openssl s_client -connect "$origin:443" -servername "$host" -verify_hostname "$host" -verify_return_error </dev/null
   ```

   A timeout from a laptop outside the origin allowlist is inconclusive. Compare observations from the authorized probe and the actual Cloudflare path.

4. **Verify through Cloudflare.** After the targeted fix, fetch the original public URL several times, confirm status and the expected body, then correlate with a new successful origin request. Record affected hosts, error count and interval. If a new certificate or listener causes additional failures, redeploy the last known good valid configuration and retest each backend.

[Cloudflare cheat sheet](README.md) · [Error 522](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-5xx-errors/error-522/) · [Error 525](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-5xx-errors/error-525/) · [Error 526](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-5xx-errors/error-526/) · [Cloudflare IP ranges](https://www.cloudflare.com/ips/)
