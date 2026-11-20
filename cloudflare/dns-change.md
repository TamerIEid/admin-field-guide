# Move one web hostname to a new origin

**Scope.** Change one existing A record in an active Cloudflare zone. Know whether it is proxied or DNS-only, its old value and TTL, and who can return traffic to the old origin. This procedure assumes a single backend target and no load balancer or origin override. Map those first if present.

1. **Save the rollback values.** In DNS → Records, record the name, type, content, proxy status and TTL privately. Inspect sibling A and AAAA records, redirects and any origin rule for this name. For a DNS-only change, clients may keep the old address for the previous TTL. Keep both origins capable of serving compatible data through that interval.
2. **Test the new origin before changing DNS.** Use the real host and new address privately. The following example preserves HTTP Host, TLS SNI and certificate checks. Run it from an authorized origin test location. For a private CA, use its approved CA bundle with `--cacert`.

   ```bash
   host=shop.example.com
   new_origin=192.0.2.40
   curl --resolve "$host:443:$new_origin" --max-time 12 -sS -i "https://$host/health"
   ```

   Expect a status and **release marker unique to the new target**. A redirect to another host or a generic 200 needs investigation. If the origin admits only Cloudflare or uses authenticated origin pulls, use the existing trusted probe or staged edge route.

3. **Change the one record.** In the zone’s DNS records, edit the selected A record’s address and save. Preserve the intended proxy status and other fields. Read the saved value back. Keep mail records and unrelated hosts outside this change.
4. **Verify both DNS and user traffic.** For a DNS-only name, query an assigned authoritative nameserver, then independent recursors. For a proxied name, public DNS normally shows edge IPs. Confirm the saved origin in Cloudflare, then prove a request reached it via a fresh origin log entry or an uncached release marker.

   ```bash
   auth_ns=ns1.example.net
   dig @"$auth_ns" "$host" A +noall +comments +answer
   dig @1.1.1.1 "$host" A +noall +comments +answer
   dig @8.8.8.8 "$host" AAAA +noall +comments +answer
   curl --max-time 12 -sS -i "https://$host/health"
   ```

   Repeat A and AAAA at both resolvers if either family is in use. Also fetch a representative user page and check its content. Watch the old and new origins across the change window.
5. **Rollback trigger.** If the new origin cannot serve the expected marker, shows TLS errors or loses required writes, restore the recorded record values and verify the old target through the same checks. Coordinate data reconciliation before directing writes back to a database that may have diverged.

[Cloudflare cheat sheet](README.md) · [Manage DNS records](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/) · [Proxied and DNS-only responses](https://developers.cloudflare.com/dns/proxy-status/)
