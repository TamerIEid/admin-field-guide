# Find out why Magento scheduled jobs are late

**Use when** catalog updates, scheduled emails or another known job are late. You need the app owner’s CLI, the expected cron cadence, and read-only database access. Keep the investigation to the scheduler node on a multi-node installation.

1. **Identify the scheduler and job.** On a crontab-managed deployment inspect `crontab -l` as the filesystem owner. On a managed service inspect its scheduled-job configuration and history. Confirm the release path, PHP executable and most recent invocation. Compare timestamps in UTC.
2. **Read the schedule, bounded to the incident.** Run the following in an approved read-only SQL session. Substitute the installation’s table prefix if present and the observed job code for the example.

   ```sql
   SELECT job_code, status, scheduled_at, executed_at, finished_at
   FROM cron_schedule
   WHERE job_code = 'indexer_update_all_views'
     AND scheduled_at BETWEEN UTC_TIMESTAMP() - INTERVAL 2 HOUR AND UTC_TIMESTAMP()
   ORDER BY scheduled_at DESC, schedule_id DESC
   LIMIT 25;
   ```

   | Observation | What to check next |
   | --- | --- |
   | New success rows, recent pending rows | Compare the age of the oldest overdue row with the normal runtime. A single sample can catch a job between ticks. |
   | Mostly missed or old pending across several job codes | Check scheduler heartbeat, maintenance windows, permissions, PHP path and overlapping runners. |
   | One code repeatedly errors while others finish | Read the matching exception in `var/log/exception.log` and cron log. Identify that job’s dependency. |
   | Old running row | Check whether the process and its DB work are still active with the app/DB owner. Preserve the row for diagnosis. |

3. **Restore the cause.** For a confirmed stopped scheduler, re-enable its existing definition through the system that owns it. For a confirmed failing job, repair the reported dependency through its service owner. Manual cron runs can dispatch customer-facing work. A clean stop is to hand the owner the first missed UTC tick, affected code and error when the job has side effects or may already be running.
4. **Wait for successive scheduler invocations.** One pass can create schedules and a later pass executes due jobs. Re-run the query after two expected ticks and again after the job’s normal runtime. Look for a **new** success row, a falling overdue backlog, and an updated storefront item or other expected business outcome. Record any individual jobs that require separate reconciliation before replay.

[Magento cheat sheet](README.md) · [Adobe cron setup, logging and schedule table](https://experienceleague.adobe.com/en/docs/commerce-operations/configuration-guide/cli/configure-cron-jobs)
