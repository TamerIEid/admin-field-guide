# Close inbound TCP 22 on one EC2 instance

Begin after the [two-session test](README.md#5-open-and-prove-two-native-sessions). Keep native SSM session A open. Use a separate **workstation** terminal for the AWS commands. If another operator owns EC2 network changes, have them confirm their account and Region and use their authorized profile for the edit.

## 1. Record the current path and all attached groups

1. Record the application’s baseline health and the expected direct instance addresses. From each formerly authorized path (for example the admin VPN or bastion), run the matching probe in step 4 **before the change**. Use a fresh connection to the instance address. A CDN hostname or an unrelated load balancer tests a different endpoint.
2. List every network interface (ENI) and security group attached to this instance. Record public/private IPv4 and IPv6 destinations that are in scope from **EC2 → Network Interfaces**.

   ```sh
   aws ec2 describe-network-interfaces --filters "Name=attachment.instance-id,Values=$TargetId" --query 'NetworkInterfaces[].{ENI:NetworkInterfaceId,Private:PrivateIpAddress,Groups:Groups[].GroupId}' --output json
   ```

3. For **each distinct group** from the result, substitute its ID below. Read every ingress rule and save its rule ID, source, protocol, from/to ports and description privately. Also inspect the member interfaces to find other workloads that would inherit the change. Check launch templates or infrastructure-as-code for intended future users of the group.

   ```sh
   aws ec2 describe-security-group-rules --filters "Name=group-id,Values=sg-0123456789abcdef0" --query 'SecurityGroupRules[?!IsEgress].{Rule:SecurityGroupRuleId,Protocol:IpProtocol,From:FromPort,To:ToPort,IPv4:CidrIpv4,IPv6:CidrIpv6,SourceGroup:ReferencedGroupInfo.GroupId,PrefixList:PrefixListId,Description:Description}' --output json
   aws ec2 describe-network-interfaces --filters "Name=group-id,Values=sg-0123456789abcdef0" --query 'NetworkInterfaces[].{ENI:NetworkInterfaceId,Instance:Attachment.InstanceId,Type:InterfaceType}' --output table
   ```

   | Inbound rule | Does it allow port 22? | Action |
   | --- | --- | --- |
   | TCP 22–22 from IPv4, IPv6, a security group or a prefix list | Yes, for matching sources | Identify its users and rollback source. A private-source rule still gives its source SSH access. |
   | TCP range containing 22, such as 20–25 | Yes | Preserve each required non-SSH port first. Replace the broad rule only after dependent services are covered. |
   | All traffic (protocol `-1`) | Yes | Work with the owner to narrow it. Removing an additional exact-22 rule alone leaves SSH permitted. |
   | UDP 22, TCP 443 or an egress rule | No inbound TCP 22 grant | Leave it in place for this change. |

Security groups combine their allows across all groups on an interface. Repeat this check for every attached interface. A shared group can serve databases, load balancers, other instances or future replacements. For a shared group that must keep SSH for others, prepare an instance-specific group with equivalent required application ingress and egress, preserve dependencies that reference the old group’s identity, and replace only the target interface’s group membership through its owner. Merely adding a stricter group leaves the old allow effective. [VPC security group rules](https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html) · [EC2 group changes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/changing-security-group.html)

## 2. Prepare recovery before the edit

Save the original group membership per interface and the exact rule definitions. Confirm who can reauthorize a narrow trusted source after a disconnect and how they will reach the target. For an IaC-managed group, prepare the change and rollback in the owning Terraform, CloudFormation or equivalent configuration. Preserve a path to the EC2 API that works independently of the instance.

If **all** interfaces already lack an inbound TCP 22 grant, go directly to verification. This is common on Windows Server. If a broad rule remains, report its scope until its owner can safely narrow it.

## 3. Remove the confirmed SSH grant

For a **dedicated group** and an exact TCP 22 rule, choose either path:

- **Console.** In EC2 → Security Groups, select the recorded group, choose **Edit inbound rules**, remove the row matching the saved rule ID and source, then save. Work one reviewed change at a time.
- **CLI.** Replace **both** example IDs with values seen together in step 1. First add `--dry-run` to the command. AWS returns a nonzero `DryRunOperation` when permission is sufficient or `UnauthorizedOperation` when it is missing. A dry run only checks authorization. When the IDs and impact match, run the actual command once:

  ```sh
  aws ec2 revoke-security-group-ingress --group-id sg-0123456789abcdef0 --security-group-rule-ids sgr-0123456789abcdef0
  ```

Read the rules back after each change. Include IPv6 or source-group grants if present. If more than one service uses a rule, use the replacement plan from step 1. If a request times out, inspect the group before retrying. [Revoke ingress by rule ID](https://docs.aws.amazon.com/cli/latest/reference/ec2/revoke-security-group-ingress.html)

## 4. Prove access, closure and application health

1. **New management access succeeds.** From a fresh workstation terminal, restore your operator profile, Region and target ID. Start another native session and repeat the target hostname and OS identity checks. Session A surviving the change gives no evidence about reconnecting.

   ```sh
   aws ssm start-session --target "$TargetId"
   ```

2. **A new direct connection to 22 fails.** Use the same source, target address and address family as the baseline. Repeat for each formerly permitted source/path that you can test, including IPv6 where used. Replace the documentation address. For a private instance, run the probe from the previously allowed VPN, host or bastion.

   | Probe computer | Fresh TCP check | Pass after the edit |
   | --- | --- | --- |
   | Linux with netcat | `nc -vz -w 5 192.0.2.40 22` | No TCP connection. |
   | macOS | `nc -vz -G 5 192.0.2.40 22` | No TCP connection. |
   | Windows PowerShell | `Test-NetConnection -ComputerName 192.0.2.40 -Port 22 -InformationLevel Detailed` | `TcpTestSucceeded : False`. |

   An SSH banner, login prompt or “permission denied (publickey)” means the network connection still succeeds. Previously established SSH flows may survive a tracked rule change. A timeout alone can also reflect routing or a host firewall. Pair the fresh probe with the full security-group readback. If a source could never connect before, document its baseline and the limits of that probe. [EC2 connection tracking](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-connection-tracking.html)

3. **The application still works.** Repeat the same pre-change health check and one representative transaction-safe operation, for example fetching a product page with the expected content. Confirm any SSH-dependent jobs that were migrated. Record the instance, Region, rule IDs, coverage of former paths, session IDs, UTC times and application result. Type `exit` in the remaining native shells when finished.

## If access or application health regresses

- **New SSM sessions fail.** Keep any proven working session while the owner diagnoses the failure. From the independent EC2 control plane, temporarily reauthorize TCP 22 in the correct dedicated group **only for the approved recovery source**. In the console add **SSH → TCP 22** with the known admin IPv4 /32, IPv6 /128, VPN CIDR or bastion security group as appropriate. Confirm the source identity actually used on that path. AWS assigns a new rule ID. If SSH was already absent on Windows, use its recorded recovery channel.
- **A dependent service fails.** Restore the affected application rule or recorded interface membership through its owner. Check the same application request again. Restore intended state in IaC before another deployment.
- **Verify recovery.** Open a new connection from the recovery source and check host identity. If the host listener has also been retired, use the independently tested OS recovery path to restore it first. Give any temporary rule an owner and removal time. Repeat the two-session and closure tests after the cause is fixed.

[Return to the migration guide](README.md) · [Optional host-level shutdown](retire-ssh.md)
