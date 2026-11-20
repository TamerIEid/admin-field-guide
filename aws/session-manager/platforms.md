# Set up the workstation and the EC2 target

Choose **one workstation row** and **one target row**. For example, if you administer an Ubuntu instance from a MacBook, install the macOS plugin on the MacBook and check the Ubuntu agent on the instance.

## Install the workstation tools

1. Run `aws --version` and `session-manager-plugin --version`. Expect `aws-cli/2.x` and a plugin version. Install either missing component using the appropriate row. [AWS CLI v2 installers](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

   | Your computer | AWS CLI v2 | Session Manager plugin |
   | --- | --- | --- |
   | Linux | Install the AWS CLI v2 Linux bundle for `x86_64` or `aarch64`. Check `uname -m`. | Use the official DEB or RPM for that architecture. On Debian/Ubuntu, download the indicated DEB and run `sudo dpkg -i session-manager-plugin.deb`. [Linux package selection](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-linux-overview.html) · [Debian/Ubuntu steps](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-debian-and-ubuntu.html) |
   | macOS | Install AWS’s macOS CLI v2 PKG. | Choose the signed plugin PKG for Apple silicon (`arm64`) or Intel (`x86_64`). Run the installer and follow AWS’s symlink step if the executable is outside PATH. [macOS package and PATH steps](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html) |
   | Windows | Install AWS CLI v2 using its Windows MSI. Open a new PowerShell window. | Run AWS’s `SessionManagerPluginSetup.exe`, accept the default path, reopen PowerShell and repeat both version checks. [Windows installer](https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-windows.html) |

2. Use your organization’s existing profile. If using IAM Identity Center for the first time, create the named profile with `aws configure sso --profile ops-session` using the start URL, SSO Region, account and role provided by the administrator. Substitute your actual profile, workload Region and instance ID in the block for your workstation. The workload and SSO Regions can differ. [IAM Identity Center with the CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)

   **Linux or macOS workstation — Bash or zsh**

   ```bash
   export AWS_PROFILE=ops-session
   export AWS_REGION=us-east-1
   export AWS_PAGER=""
   TargetId=i-0123456789abcdef0
   ```

   **Windows workstation — PowerShell**

   ```powershell
   $env:AWS_PROFILE = 'ops-session'
   $env:AWS_REGION = 'us-east-1'
   $env:AWS_PAGER = ''
   $TargetId = 'i-0123456789abcdef0'
   ```

3. For an SSO profile, run `aws sso login --profile ops-session` with your actual profile name. Check `aws sts get-caller-identity`, compare the returned account and role with the change record, then continue in that terminal. Use a read-only profile only for inventory. Starting a session requires an operator role with session privileges.

## Check the agent on the target

Use the current approved access path to the **EC2 instance**. These commands belong on the target. Some AMIs already contain SSM Agent. Use the installed package’s service manager and avoid running two copies of the agent. [AWS agent status commands](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent-status-and-restart.html)

### Linux target

For an RPM-based systemd installation such as Amazon Linux 2023, inspect the service, then enable and start it if required:

```bash
systemctl status amazon-ssm-agent --no-pager
sudo systemctl enable --now amazon-ssm-agent
systemctl is-active amazon-ssm-agent
systemctl is-enabled amazon-ssm-agent
```

If the unit is missing on Amazon Linux, install AWS’s RPM for the instance architecture, then repeat the checks. On **Ubuntu using Snap**, check `snap list amazon-ssm-agent`. If there is no agent installation, use `sudo snap install amazon-ssm-agent --classic`. For the Snap package run:

```bash
sudo snap start --enable amazon-ssm-agent
snap services amazon-ssm-agent
```

Expect `active` and startup enabled. Inspect `/var/log/amazon/ssm/amazon-ssm-agent.log` for registration or connection errors. [Amazon Linux packages](https://docs.aws.amazon.com/systems-manager/latest/userguide/agent-install-al2.html) · [Ubuntu Snap installation](https://docs.aws.amazon.com/systems-manager/latest/userguide/agent-install-ubuntu-64-snap.html)

### macOS target on EC2 Mac

Check the launch daemon and recent log entries. A loaded, running daemon should show its process state:

```bash
sudo launchctl print system/com.amazon.aws.ssm
sudo tail -n 30 /var/log/amazon/ssm/amazon-ssm-agent.log
```

If the plist is missing, install AWS’s signed agent PKG for the EC2 Mac’s architecture (`darwin_arm64` or `darwin_amd64`). If installed but unloaded, use AWS’s `sudo launchctl load -w /Library/LaunchDaemons/com.amazon.aws.ssm.plist`. If loaded but stopped, run `sudo launchctl start com.amazon.aws.ssm`. Check the daemon and log again. [EC2 Mac agent installation](https://docs.aws.amazon.com/systems-manager/latest/userguide/manually-install-ssm-agent-macos.html)

### Windows Server target

Open **PowerShell as Administrator** on the instance. If `Get-Service` reports that the service does not exist, install AWS’s Windows SSM Agent from the linked instructions and retry. For an installed service:

```powershell
Get-Service -Name AmazonSSMAgent
Set-Service -Name AmazonSSMAgent -StartupType Automatic
Start-Service -Name AmazonSSMAgent
Get-Service -Name AmazonSSMAgent | Select-Object Name, Status, StartType
Get-Content "$env:ProgramData\Amazon\SSM\Logs\amazon-ssm-agent.log" -Tail 30
```

Expect `Running` and `Automatic`. A Windows target can provide a native Session Manager PowerShell shell without having OpenSSH Server installed. The cutover’s network change concerns port 22. RDP on TCP 3389 is a separate access decision. [Windows agent installation](https://docs.aws.amazon.com/systems-manager/latest/userguide/manually-install-ssm-agent-windows.html) · [AWS agent log paths](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent-logs.html)

[Return to the two-session test](README.md#5-open-and-prove-two-native-sessions)
