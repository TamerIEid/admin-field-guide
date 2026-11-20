# Review and rehearsal notes

**20 November 2026.** This edition covers systemd Linux, Magento Open Source / Adobe Commerce 2.4 CLI deployments, single-site WordPress, Cloudflare DNS/CDN, and AWS CLI v2. The examples use synthetic resources. The platform-specific acceptance checks below are suitable for an administrator reviewing the guide before publication.

| Area | Evidence collected for this edition | What to check on your own stack |
| --- | --- | --- |
| Linux | Executed the file restore drill, including deliberate damage and repair. Tested an invalid NGINX configuration and a successful reload with an isolated NGINX 1.30.7 process. | Confirm the service name, config invocation, log destination and backup recovery target on your distribution. The NGINX rehearsal used a container process. |
| WordPress | Used WordPress 7.1.5, WP-CLI 2.12.0 and an isolated MariaDB. Checked plugin version and rendered shortcode through an update and rollback. Reproduced a 500, deactivated the broken fixture, observed 200 and restored the feature. An external runner published a scheduled fixture post. | Rehearse the real plugin’s feature, migrations, web PHP version and staging delivery controls. |
| Magento | Checked commands against Adobe guidance. Ran the bounded cron query against synthetic rows in MariaDB and checked that future and unrelated jobs were excluded. | A Commerce operator should rehearse CLI index status, scope-specific pricing and release/maintenance handling on the actual edition and deployment type. |
| Cloudflare | Checked the procedures against Cloudflare’s DNS, cache and origin-error references. | Use a test hostname and a versioned marker to rehearse DNS rollback, cache-key behaviour and strict TLS. A zone change and edge purge still need a live rehearsal. |
| AWS | Checked command options with AWS CLI v2 and exercised the queries against synthetic responses, including an empty vault result and a newer incomplete point. | Verify the workload’s account, permissions, recent metric transition and backup retention in a sandbox. Provider delivery and data restoration require their own evidence. |

## Review in three passes

1. **As a new reader**, start at the [task index](README.md). Follow the [Linux file restore](linux/restore-files.md) from a fresh shell. You should catch exactly one deliberately damaged file and finish with both checks passing.
2. **As an application administrator**, run the [WordPress plugin exercise](wordpress/practice/README.md) on a disposable install. Check the article after each version change. For Magento, pick a known SKU and document website, group, currency, expected price and actual price before deciding which branch applies.
3. **As the publishing owner**, choose one Cloudflare and one AWS task for sandbox readback. Check that each example fits your platform and that every link opens from a clean checkout. Record the reviewer, platform version, date, expected result and actual result for any new rehearsal.
