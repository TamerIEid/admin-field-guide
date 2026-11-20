# A write failed with “No space left on device”

**Goal.** Identify which mount ran out of bytes or inodes, recover headroom through the owning service, and confirm that the original writer works.

1. **Find the affected mount.** Set this to an existing directory containing the failed write. Save the device, mount point, available bytes and free inodes.

   ```bash
   target=/var/log
   findmnt --target "$target"
   df -hT "$target"
   df -i "$target"
   ```

2. **Follow the evidence.** If bytes are low, inspect the largest directories on that filesystem. Start at the mount point from step 1 or a suspected subtree on it. The scans read metadata and can add I/O on a busy host. Run one at a time.

   ```bash
   scan=/var
   sudo du -xhd1 "$scan" | sort -h | tail -12
   ```

   For inode exhaustion, count entries instead. Descend into the largest directory one level at a time.

   ```bash
   sudo du -x --inodes --max-depth=1 "$scan" | sort -n | tail -12
   ```

3. **If `df` reports much more use than `du` explains**, check for open, unlinked files. Compare the DEVICE and SIZE/OFF columns with the affected mount. For example, a multi-gigabyte deleted access log held by a web worker still consumes blocks. Other explanations include snapshots, permissions and files hidden beneath a mount.

   ```bash
   sudo lsof -nP +L1
   ```

4. **Recover space through the owner.** For a confirmed deleted NGINX log on a packaged systemd host, confirm the configured log directory has its expected ownership, then signal the master to reopen its logs. For retained files, apply the service’s retention procedure to an identified, eligible set. Escalate database files, backups or an unknown writer to their owner.

   ```bash
   sudo systemctl kill --kill-who=main --signal=USR1 nginx.service
   ```

5. **Prove recovery.** Repeat both `df` commands. For the NGINX case, confirm the old descriptor disappeared from `lsof` and that one benign request produced a new access-log entry when logging is enabled. For other writers repeat one safe original operation. Record the headroom gained and check its growth again in ten minutes. A positive growth rate that consumes the gain before the next shift needs an owner now.

[Linux cheat sheet](README.md) · [GNU df](https://man7.org/linux/man-pages/man1/df.1.html) · [lsof options](https://man7.org/linux/man-pages/man8/lsof.8.html) · [NGINX log reopening](https://nginx.org/en/docs/control.html)
