# Linux daily cheat sheet

For a host using systemd, GNU tools and a shell with permission to read the relevant logs. Start as an ordinary user. Admin access may be needed for process ownership and service logs.

| Question | Check | What to look for |
| --- | --- | --- |
| Which host and boot am I examining? | `hostnamectl --static` and `uptime -s` | Match inventory and the incident window. An unexpected reboot changes where to look for logs. |
| Is the service actually up? | `systemctl --failed --no-pager` and `systemctl is-active nginx` | A failed unit or a nonzero exit narrows the search. Check the user URL even when the service is active. |
| What changed recently? | `journalctl -u nginx --since "30 min ago" --utc -n 80 --no-pager` | Find the first error near the failed request. Set the correct unit for your service. |
| Can this path still accept writes? | `df -hT /var` and `df -i /var` | Check bytes and free inodes on the mount that owns the affected path. |
| Is the host under pressure now? | `uptime`, `nproc`, `free -h` and `vmstat 1 5` | Compare load with CPU count. Read “available” memory. In vmstat use rows after the first for current CPU wait, swap activity and runnable tasks. |
| Is anything listening? | `ss -lnt` | Match the expected address and port. A loopback-only listener needs a local proxy for remote traffic. |
| Did scheduled maintenance run? | `systemctl list-timers --all --no-pager` | Compare LAST and NEXT with the schedule, then read the associated service journal for its actual result. |
| Which boot contains the error? | `journalctl --list-boots` | If the preceding boot is available, inspect it with `journalctl -b -1 -p warning --no-pager`. |

**A useful pair of observations.** A load average of 8 on a 2-vCPU VM calls for a closer look. Sustained high `wa` suggests investigating storage latency. A busy `r` queue with little idle CPU points toward CPU demand. Use the service response and its normal baseline to decide urgency.

[Disk pressure](disk-pressure.md) · [NGINX recovery](nginx-recovery.md) · [File restore drill](restore-files.md) · [systemctl manual](https://man7.org/linux/man-pages/man1/systemctl.1.html) · [journalctl manual](https://man7.org/linux/man-pages/man1/journalctl.1.html)
