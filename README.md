# Admin Field Guide

Five cheat sheets and sixteen runbooks for the person who looks after a web store and its infrastructure. Start with what the user sees. Each guide gives you a first check, tells you how to read the result, and ends with a test you can hand to the next shift.

**Try it in five minutes.** Restore two sample files into an empty directory, compare their hashes, then see the check catch a damaged file. You need a Linux shell and no cloud account. [Run the restore drill](linux/restore-files.md)

**Have a disposable WordPress site?** Build two tiny plugin ZIPs locally. Watch one post display version 1, version 2, then version 1 again after rollback. [Run the plugin rehearsal](wordpress/practice/README.md)

## Find a task

| At the start of a shift | When something needs attention |
| --- | --- |
| [Linux cheat sheet](linux/README.md) | [Disk or inodes running out](linux/disk-pressure.md) · [NGINX reload or startup failed](linux/nginx-recovery.md) · [Prove a file restore](linux/restore-files.md) |
| [Magento cheat sheet](magento/README.md) | [A storefront price is wrong](magento/stale-price.md) · [Scheduled jobs are late](magento/cron-backlog.md) · [503 after a release](magento/maintenance-503.md) |
| [WordPress cheat sheet](wordpress/README.md) | [Recover from a plugin fatal error](wordpress/plugin-fatal.md) · [Rehearse one plugin update](wordpress/update-plugin.md) · [A scheduled post missed its time](wordpress/missed-post.md) |
| [Cloudflare cheat sheet](cloudflare/README.md) | [Move one web DNS record](cloudflare/dns-change.md) · [An asset still shows old bytes](cloudflare/stale-asset.md) · [Trace a 522, 525 or 526](cloudflare/origin-errors.md) |
| [AWS cheat sheet](aws/README.md) | [An EC2 site is unreachable](aws/ec2-unreachable.md) · [Trace a CloudWatch alarm](aws/alarm-history.md) · [Check a workload’s latest backup](aws/backup-freshness.md) |

**Retiring direct SSH access to EC2?** Set up AWS Systems Manager Session Manager from Linux, macOS or Windows, prove a second shell works, then close and verify inbound TCP 22. [Step-by-step migration](aws/session-manager/README.md)

## First ten minutes on shift

1. **Open the user path.** Fetch a known public page and look for a specific marker, such as the store name and an expected product price. Compare the response and timing with the last healthy check from the same location.
2. **Check what changed.** Match the first bad UTC timestamp to a deployment, DNS edit, plugin update or maintenance window. Write down the last known good response.
3. **Check the work users cannot see.** Compare the last successful scheduled job and usable backup with their agreed intervals. A storefront can serve pages while jobs accumulate.
4. **Pick one owner and next check.** A full disk starts on Linux. A healthy origin serving old content starts in the application. Correct content at the origin and old bytes at the edge go to the Cloudflare runbook.

## Working through a guide

Commands use Bash on GNU/Linux unless a guide names another shell or target OS. Replace example hosts, paths, IDs and profile names with values from your inventory. Run the blocks in order in the indicated terminal. Each runbook identifies the commands that change state and the environment they target. Times in examples are UTC. Success means a user-visible check or a recorded diagnosis.

**Shift note you can copy**

```text
UTC window and environment:
Affected user action and scope:
Last good / first bad result:
Change or evidence that explains it:
What I did and how I verified it:
Remaining risk, next check time and owner:
```

For example, “14:05–14:13 UTC, staging. A guest saw the old logo. Origin returned the release hash. The edge returned the previous hash and HIT. After a single-URL purge the same edge request matched the release twice. Jo checks the second region at 14:20.” This is an illustrative handoff.

[Review evidence and rehearsal limits](REVIEW.md)
