# WordPress daily cheat sheet

For a single-site install with WP-CLI. Run as the site’s filesystem owner from the intended WordPress root. Match `wp option get home` to your inventory before making a change. On multisite, confirm the blog with `--url` and check network activation with the network administrator.

| Question | Command or screen | Read the result |
| --- | --- | --- |
| Right install and site? | `wp core version` and `wp option get home` | Match the deployed version and public address. `wp option get siteurl` can legitimately include a different path. |
| Which plugins are active or awaiting updates? | `wp plugin list --fields=name,status,version,update` | Compare with the release record. Updates may come from a vendor or a deployment pipeline. |
| Does core match the published release? | `wp core verify-checksums` | Needs access to WordPress.org. Investigate named differences against the deployment manifest. Plugins, uploads and the database have separate integrity checks. |
| Are tasks moving? | `wp cron event list --fields=hook,next_run_gmt,recurrence` | Compare recurring and one-off hooks with UTC now and the normal runner interval. |
| What does PHP report? | Tools → Site Health → Info → Server | Compare the web PHP version and limits with the host deployment. `wp --info` identifies the separate CLI runtime. |
| What failed on the request? | Hosting PHP error log and the access log for the same minute | Match route, timestamp and the first fatal error. Keep diagnostics private and error display off for visitors. |
| Is recovery possible today? | Backup console → last successful database and files job | Confirm age against the site target and find the last successful isolated application restore. Files alone omit posts and options. |

[Plugin fatal error](plugin-fatal.md) · [Single-plugin update rehearsal](update-plugin.md) · [Missed scheduled post](missed-post.md) · [Core checksums](https://developer.wordpress.org/cli/commands/core/verify-checksums/) · [WordPress backups](https://developer.wordpress.org/advanced-administration/security/backup/)
