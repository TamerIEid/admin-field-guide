# Check whether an EBS volume has a recent AWS Backup recovery point

**Scope.** One EBS volume protected by periodic AWS Backup snapshots in a known account, vault and Region. Bring its recovery point objective (RPO), the maximum acceptable age of recovered data. Confirm the profile and Region using the [AWS cheat sheet](README.md).

1. **Find the latest completed point for the exact volume.** Replace both identifiers. The query sorts completed points by creation time so an older job finishing late cannot appear newer. JSON output lets the CLI combine paginated results.

   ```bash
   vault=example-vault
   volume_arn='arn:aws:ec2:us-east-1:111122223333:volume/vol-0123456789abcdef0'
   aws backup list-recovery-points-by-backup-vault --backup-vault-name "$vault" --by-resource-arn "$volume_arn" \
     --query 'sort_by(RecoveryPoints[?Status==`"COMPLETED"`], &CreationDate)[-1].{Point:RecoveryPointArn,Created:CreationDate,Finished:CompletionDate,State:Status}' --output json
   ```

2. **Compare capture age with the RPO.** Use UTC. Example: now 14:00, point created 06:15, completion 06:40. Its creation age is **7h 45m**. For a six-hour RPO, flag a **1h 45m gap** and check the next job. Creation time is an operational proxy for snapshot age; the workload’s own consistency marker gives stronger data-age evidence.
3. **If the result is empty or too old, inspect jobs.** Set a start time covering at least two expected backup windows. Include the job state and service message in the owner handoff.

   ```bash
   since_utc=$(date -u -d '3 days ago' +%FT%TZ)
   aws backup list-backup-jobs --by-resource-arn "$volume_arn" --by-created-after "$since_utc" \
     --query 'sort_by(BackupJobs,&CreationDate)[].{Created:CreationDate,State:State,Message:StatusMessage,Vault:BackupVaultName}' --output json
   ```

   No matching job calls for a check of the plan’s resource assignment, tags, schedule and Region. A running job can still be inside its window. For a failed or expired job, inspect its service message and timing. Verify the source or copy vault for cross-Region plans.
4. **Finish with two answers.** Record the latest known capture age and the last successful application restore date. For a restore drill, use the selected point to create a separate volume in a test instance’s AZ, validate known data on an isolated host and record elapsed time. Use the filesystem’s safe read-only/no-replay procedure for the restored volume. Confirm cleanup of the temporary resources and any expected cost. A completed point with no recent restore test leaves recoverability unverified.

[AWS cheat sheet](README.md) · [Vault recovery point CLI](https://docs.aws.amazon.com/cli/latest/reference/backup/list-recovery-points-by-backup-vault.html) · [Backup jobs CLI](https://docs.aws.amazon.com/cli/latest/reference/backup/list-backup-jobs.html) · [Restore an EBS volume](https://docs.aws.amazon.com/aws-backup/latest/devguide/restoring-ebs.html)
