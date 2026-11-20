# Stop listening for SSH on the host

Closing every inbound security-group grant completes the **EC2 network** cutover. Use this extra step when the goal also includes **no port 22 listener inside the OS**. Open a fresh native SSM shell after the network change and verify it has the required administrative privileges. Confirm SSH/SFTP-based jobs have moved. Record the current active and startup settings before changing them.

**Recovery prerequisite.** Verify an independent way to administer this OS if SSM goes offline, such as your tested platform recovery procedure or an established Windows management path. Reopening a security group alone cannot start a stopped SSH service. If your only tested fallback needs the SSH daemon, keep the listener and use the completed network cutover.

## Linux with systemd

1. Identify what owns the listening socket and capture the unit states. Some distributions use `ssh.service`, others `sshd.service`. Ubuntu can also use socket activation, where systemd owns the listener. Missing unit names are expected when checking alternatives.

   ```bash
   sudo ss -lntp 'sport = :22'
   systemctl list-unit-files 'ssh*.service' 'ssh*.socket'
   systemctl show -p Id -p ActiveState -p UnitFileState ssh.socket ssh.service sshd.service
   ```

2. In the SSM shell, choose the **one** procedure matching the observed setup. Disabling a service can terminate SSH users or their work. Coordinate existing sessions first.

   | Observed owner/startup path | Stop the listener and prevent startup on boot |
   | --- | --- |
   | `sshd.service` is the standalone enabled service | `sudo systemctl disable --now sshd.service` |
   | `ssh.service` is the standalone enabled service | `sudo systemctl disable --now ssh.service` |
   | `ssh.socket` is enabled and activates `ssh.service` | Run `sudo systemctl disable --now ssh.socket`, then `sudo systemctl stop ssh.service`. If the service was also independently enabled, `sudo systemctl disable ssh.service`. |

   If another socket, container, custom unit or configuration manager owns port 22, change its actual owner and persistence setting.
3. Repeat `sudo ss -lntp 'sport = :22'`. Expect a header with no listener rows. Recheck the previously active/enabled units and open a new native SSM session. For rollback, restore the **recorded** unit states. For a formerly enabled standalone service use `sudo systemctl enable --now sshd.service` or `ssh.service` as appropriate. For a formerly enabled socket use `sudo systemctl enable --now ssh.socket` and let it activate its service. If a unit was active but disabled at boot, restore only its running state with `systemctl start`. [systemctl manual](https://man7.org/linux/man-pages/man1/systemctl.1.html) · [Ubuntu OpenSSH and socket activation](https://documentation.ubuntu.com/release-notes/24.04/)

## EC2 Mac with macOS Remote Login

1. From the native SSM session record `sudo systemsetup -getremotelogin` and `sudo lsof -nP -iTCP:22 -sTCP:LISTEN`. A launchd-owned listener may be visible before an SSH process starts.
2. If Remote Login is on and its SSH/SFTP users have moved, run `sudo systemsetup -setremotelogin off` and answer the prompt. On macOS versions or managed configurations that restrict this operation, use an approved administrator session in **System Settings → General → Sharing → Remote Login**, or the device-management owner’s workflow.
3. Confirm Remote Login reports `Off`, the `lsof` command shows no listener and a new SSM session works. If it was previously on, rollback uses `sudo systemsetup -setremotelogin on` or the same Sharing control. Recheck the listener and the explicitly permitted recovery path. [Apple Remote Login settings](https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac) · [Apple systemsetup commands](https://support.apple.com/guide/remote-desktop/apd95406b8d/mac)

## Windows Server with OpenSSH Server

1. In an elevated native PowerShell session, inspect the service and the port. If the service is absent and the listener query returns nothing, record that result and finish. If a different process listens on 22, identify its owning service before changing anything.

   ```powershell
   Get-Service -Name sshd -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType
   Get-NetTCPConnection -State Listen -LocalPort 22 -ErrorAction SilentlyContinue | Select-Object LocalAddress, LocalPort, OwningProcess
   ```

2. For a confirmed OpenSSH Server service, record its original startup setting (including delayed automatic start, if used) and whether it is running. Once its users have moved, stop it and disable automatic starts:

   ```powershell
   Stop-Service -Name sshd -ErrorAction Stop
   Set-Service -Name sshd -StartupType Disabled -ErrorAction Stop
   Get-Service -Name sshd | Select-Object Name, Status, StartType
   Get-NetTCPConnection -State Listen -LocalPort 22 -ErrorAction SilentlyContinue
   ```

3. Expect `Stopped`, `Disabled`, no listener rows, and a fresh SSM PowerShell session. For rollback, restore the saved startup type in Services (`services.msc`) and start `sshd` only if it was previously running. For the common Automatic + Running baseline the commands are `Set-Service -Name sshd -StartupType Automatic` and `Start-Service -Name sshd`. Recheck its status and the approved recovery path. Keep RDP configuration under its own access plan. [Microsoft OpenSSH Server administration](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)

[Network verification and rollback](close-port-22.md) · [Session Manager migration](README.md)
