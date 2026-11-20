# Recover an NGINX configuration change

**Use when** a packaged NGINX systemd service failed to start or a reload left the old site serving. Have the last working config revision, a known harmless URL with a recognizable body, and access to the deployment owner. Commands assume a single NGINX master using the packaged config.

1. **Read the unit and its log before retrying.** Find the unit’s config path and executable in `systemctl cat nginx`. If they differ from the defaults, use the same binary, prefix and `-c` config file for the test below.

   ```bash
   systemctl is-active nginx
   systemctl status nginx --no-pager -l
   sudo journalctl -u nginx --since "20 min ago" --utc -n 60 --no-pager
   sudo nginx -t
   ```

2. **Read the first specific error.** A missing include, unknown directive or unreadable certificate normally names a file. A bind error at startup calls for `sudo ss -lntp` and the service that owns the port. If the config test passes but the page returns 502, follow the upstream address in the error log and check its listener. Repeated NGINX restarts add little evidence.
3. **Apply the smallest recovery.** Restore the affected config from the known working revision through the normal deployment mechanism. Confirm the corrected revision and run `sudo nginx -t` again. Stop on any failure. When it passes, choose the action for the observed state.

   | Observed service state | Action |
   | --- | --- |
   | Active with old workers serving | `sudo systemctl reload nginx` |
   | Inactive or failed, port available, and this host should serve | `sudo systemctl start nginx` |

4. **Verify the original route.** Replace the host and path with the monitored origin route. The example tests the local TLS listener with the correct hostname and SNI. Use the service’s trusted CA if it uses a private issuer.

   ```bash
   host=shop.example.com
   curl --resolve "$host:443:127.0.0.1" --max-time 10 -sS -i "https://$host/health"
   ```

   Compare the status **and body marker** with the expected release. Repeat from the public path without `--resolve` and inspect fresh errors. Record the config revision, both results and the UTC time. If the old revision also fails, keep the healthy upstream or current serving nodes in place and escalate with the first error.

[Linux cheat sheet](README.md) · [NGINX command-line switches](https://nginx.org/en/docs/switches.html) · [Reload behaviour](https://nginx.org/en/docs/control.html)
