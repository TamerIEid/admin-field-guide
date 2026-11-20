# A scheduled WordPress post missed its publication time

**Goal.** Determine whether the issue is scheduling, dispatch or a single callback, and prove the next scheduled post publishes. Use the editor’s expected UTC time and the post ID from the editing URL. This guide covers core WP-Cron on a single site.

1. **Check the post and clock.** Use the exact post ID. Confirm the site timezone under Settings → General and compare the GMT field with UTC now.

   ```bash
   post_id=123
   date -u
   wp post get "$post_id" --fields=ID,post_status,post_date_gmt
   wp cron event list --fields=hook,next_run_gmt,recurrence
   ```

   A post with status `future` and a future GMT timestamp is scheduled correctly. An overdue `future` post and several overdue unrelated hooks point toward dispatch. If only one hook is affected, look for a callback error or a missing scheduled event.

2. **Identify the runner.** Read `wp config get DISABLE_WP_CRON --type=constant`. An undefined constant uses WordPress’s default behaviour. With traffic-triggered cron, inspect loopback requests and Tools → Site Health for errors. `wp cron test` attempts a spawn and can start due work, so use it where dispatch is intended. With an external runner, inspect its last exit status, exact site path, user and schedule. On a quiet site the visitor-triggered runner may start late.
3. **Restore the configured runner.** Correct the failing timer, loopback path or site selection through its owner. Running all overdue jobs can send emails or trigger integrations. If an editor chooses to release one overdue post manually, first confirm its intended audience and time. That action resolves the individual post only.
4. **Prove dispatch recovered.** On staging, schedule a synthetic post a few minutes ahead in the editor. Leave the normal runner in charge. After the due time plus one runner interval, repeat `wp post get` and read the post’s public URL anonymously. Expect `publish` plus the expected title. Record scheduled time, actual observation time and how the runner was triggered. Reconcile any remaining overdue business jobs with their owners.

[WordPress cheat sheet](README.md) · [Cron event listing](https://developer.wordpress.org/cli/commands/cron/event/list/) · [WP-CLI cron spawn test](https://developer.wordpress.org/cli/commands/cron/test/) · [System scheduler integration](https://developer.wordpress.org/plugins/cron/hooking-wp-cron-into-the-system-task-scheduler/)
