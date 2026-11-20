# Prove a file restore in five minutes

**What this tests.** A fresh directory receives the expected files, with identical bytes and a usable file mode. Run these blocks in one Bash shell on GNU/Linux as an ordinary user. The drill creates only a new temporary directory and deliberately damages one disposable copy at the end.

1. **Create a known source and a separate manifest.**

   ```bash
   lab=$(mktemp -d)
   mkdir -p "$lab/source/etc-demo" "$lab/source/site" "$lab/restore"
   printf 'release=blue\n' > "$lab/source/etc-demo/app.conf"
   printf 'store ready\n' > "$lab/source/site/health.txt"
   chmod 640 "$lab/source/etc-demo/app.conf"
   (cd "$lab/source" && sha256sum etc-demo/app.conf site/health.txt) > "$lab/expected.sha256"
   tar -czf "$lab/backup.tar.gz" -C "$lab/source" etc-demo site
   tar -tzf "$lab/backup.tar.gz"
   ```

2. **Restore as a normal user into the empty destination.** These are trusted relative paths from step 1. For a real rehearsal use a selected recovery point in an isolated target, independently retained hashes or known records, and the identity the service will use. Inspect archive membership before extraction.

   ```bash
   (umask 027 && tar -xzpf "$lab/backup.tar.gz" -C "$lab/restore")
   (cd "$lab/restore" && sha256sum -c "$lab/expected.sha256")
   stat -c '%a %n' "$lab/restore/etc-demo/app.conf"
   cat "$lab/restore/site/health.txt"
   ```

   Expect two `OK` lines, mode `640`, and `store ready`. If a path is absent, the checksum fails or the application identity cannot read a required file, record the restore as failed.

3. **Prove the check detects damage.** Change one restored fixture. The second comparison should exit nonzero and name `site/health.txt`.

   ```bash
   printf 'damaged\n' > "$lab/restore/site/health.txt"
   (cd "$lab/restore" && sha256sum -c "$lab/expected.sha256")
   ```

4. **Return the fixture to its verified state.**

   ```bash
   tar -xzpf "$lab/backup.tar.gz" -C "$lab/restore" site/health.txt
   (cd "$lab/restore" && sha256sum -c "$lab/expected.sha256")
   printf 'Review directory: %s\n' "$lab"
   ```

For a real backup, also record backup age and elapsed recovery time against your agreed data-loss and downtime targets. A database-backed site needs a consistent database recovery point and an application read test. Ownership, ACLs, encryption keys and offsite retrieval each need their own verification when the workload uses them.

[Linux cheat sheet](README.md) · [GNU tar options](https://man7.org/linux/man-pages/man1/tar.1.html)
