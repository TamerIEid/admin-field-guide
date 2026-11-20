# Use AWS Systems Manager Session Manager and close inbound SSH

**The migration is complete when** an operator can open a fresh native shell on one EC2 instance and fresh TCP connections to port 22 from former SSH sources fail. A Linux, macOS or Windows computer can administer any of the three supported target families. Session Manager also works on private instances with no public IP.

| Where to start | What you will do |
| --- | --- |
| This page | Prepare the AWS permissions and network, then prove two independent sessions work. |
| [Workstation and target setup](platforms.md) | Install the plugin on your computer and check SSM Agent on Linux, EC2 Mac or Windows Server. |
| [Close port 22 and verify the result](close-port-22.md) | Inspect every attached security group, remove the intended access, prove fresh SSM access and check rollback. |
| [Stop the host’s SSH listener](retire-ssh.md) | Optionally retire OpenSSH or Remote Login on the target after the network change succeeds. |

## 1. Choose one instance and a way back

Start with a non-critical instance. From the EC2 console record its account, Region, instance ID, expected hostname, interfaces and application health check. Identify who owns the security groups and deployment configuration. Ask which jobs still use SSH, SCP, SFTP or a bastion to reach this instance. Move or test those dependencies before retiring their path.

Keep the original management path available through the session tests. Have an operator who can restore the security-group rule through the AWS control plane even if the host is unreachable. If you also plan to stop the SSH service later, that operator will need a tested way to start it inside the OS. Record the change owner and rollback trigger.

## 2. Give the instance an AWS identity

On the instance details page, inspect **IAM role**. If the node is already managed through your account’s Default Host Management Configuration, continue to step 3 and check registration in step 5. Otherwise use the instance-profile route below.

1. For an existing workload role, inspect its permissions with the IAM owner. The AWS-managed policy `AmazonSSMManagedInstanceCore` is the standard baseline for a managed node. If the role serves other instances, assess the scope before attaching anything.
2. If the instance has no role, create an IAM role with **AWS service → EC2** as its trusted entity and attach `AmazonSSMManagedInstanceCore`. In EC2 choose the instance → **Actions → Security → Modify IAM role**, select its instance profile and save. The operator making the association needs permission to pass that role.
3. Read the attached profile back. Preserve the application’s existing S3, secrets or other permissions if updating a workload role. An EC2 instance uses one attached profile at a time. [AWS instance permissions](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-instance-profile.html) · [Attach an EC2 role](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/attach-iam-role.html)

## 3. Provide the agent’s outbound path

The agent initiates HTTPS connections on **TCP 443**. For a current agent in a commercial AWS Region, it needs to resolve and reach the regional `ssm` and `ssmmessages` services. Check the DNS resolver, routes, egress policy and any TLS proxy. A private subnet can use its existing controlled outbound route or interface VPC endpoints.

For a private-endpoint setup, check **VPC → Endpoints** for `com.amazonaws.REGION.ssm` and `com.amazonaws.REGION.ssmmessages`. Enable private DNS for the endpoints and DNS support/hostnames in the VPC. The endpoint security group must accept TCP 443 **from the instance** and the instance security group must permit the corresponding egress. Check network ACL return traffic if ACLs are restrictive. Older agents in pre-2024 Regions may also use `ec2messages`. Regions launched in 2024 or later do not support that legacy service. Optional KMS encryption, CloudWatch Logs, S3 logging or agent downloads can need additional endpoint access and permissions. [VPC endpoint setup](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-create-vpc.html) · [Regional message services](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-setting-up-messageAPIs.html)

## 4. Set up the human operator and the two machines

1. Find the operator’s existing IAM Identity Center permission set or assumed IAM role for the target account. Have its owner adapt the AWS CLI example for a single managed node. Replace the account, Region, instance and session document ARNs with the intended values. Scope `ssm:StartSession` to that target and allowed native shell document. Keep `ssmmessages:OpenDataChannel`, `ssm:ResumeSession` and `ssm:TerminateSession` scoped to the caller’s own sessions as shown in AWS’s example. [AWS operator IAM examples](https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-restrict-access-quickstart.html)
2. Include the inventory reads used here: `ssm:DescribeInstanceInformation`, `ec2:DescribeNetworkInterfaces` and `ec2:DescribeSecurityGroupRules`. Apply the permission set to the intended account or update the role through its owner, then refresh the operator’s login. A separate network owner can perform the security-group edit.
3. Check the OS identity on entry. A native session can provide elevated OS access. If your organization uses Run As, verify that the configured local account exists and has the privileges needed for this task. [Run As on Linux and macOS](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-preferences-run-as.html)

On your workstation install AWS CLI v2 and the Session Manager plugin. On the instance verify SSM Agent is installed, running and enabled to survive a restart. Choose the right instructions for each machine. [Linux, macOS and Windows steps](platforms.md)

## 5. Open and prove two native sessions

Run these commands on your **workstation** after setting the profile, Region and `$TargetId` using the platform instructions. The AWS CLI commands work in Bash, zsh and PowerShell. Use the same settings in each new terminal.

```sh
aws sts get-caller-identity --query '{Account:Account,Role:Arn}' --output json
aws ssm describe-instance-information --filters "Key=InstanceIds,Values=$TargetId" --query 'InstanceInformationList[].{ID:InstanceId,Status:PingStatus,OS:PlatformName,Agent:AgentVersion,LastPing:LastPingDateTime}' --output table
aws ssm start-session --target "$TargetId"
```

Confirm the account and role before starting. Look for the exact ID, **Online**, the expected platform and a recent ping. An empty row calls for checking scope and registration. Once the shell opens, run the commands for the **target**:

| Target | In the remote session | Expected evidence |
| --- | --- | --- |
| Linux | `hostname`, `id -un`, `uname -s` | Expected hostname, authorized OS user, `Linux`. |
| EC2 Mac | `hostname`, `id -un`, `sw_vers -productVersion` | Expected Mac, OS user and macOS version. |
| Windows Server | `hostname`, `whoami`, `$PSVersionTable.PSVersion` | Expected Windows host, OS identity and a working PowerShell shell. |

Leave session A available. Open a second workstation terminal under the **usual on-call role**, set the same profile/Region/ID and run `aws ssm start-session --target "$TargetId"` again. Repeat the identity checks, capture both session IDs privately, then type `exit` in B. Confirm the operator can end a session. A second prompt opened from session A would use the same connection and would miss a broken reconnect path. If your organization requires transcripts, check that a harmless marker from a standard session appears in the configured destination. CloudTrail session API events document the caller and time; command transcripts require separate S3 or CloudWatch Logs configuration. [Starting sessions](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html) · [Session logging](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-logging.html)

**Both sessions passed?** Continue with [close inbound TCP 22, test and roll back](close-port-22.md).

## If a session fails

| Symptom | Check next |
| --- | --- |
| `session-manager-plugin` missing | Open a new workstation terminal and verify `session-manager-plugin --version`. The Systems Manager console’s Session Manager → Start session can help isolate a local installation issue. |
| `AccessDeniedException` | Confirm caller, account, Region, target tags, shell document and own-session permissions. If preferences require a customer KMS key, check both the operator and node permissions. |
| Empty inventory or `TargetNotConnected` | Confirm instance ID, running agent, instance-profile credentials, outbound 443, DNS and endpoint security groups. Inspect the [agent log for the target OS](platforms.md#check-the-agent-on-the-target). |
| Node online, session opens then exits | Inspect the agent log at that UTC time, the Run As account or shell profile, and required encryption/logging destinations. Try the same native shell through the console to isolate workstation issues. |

[AWS cheat sheet](../README.md) · [Session Manager prerequisites](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html)
