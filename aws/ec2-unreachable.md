# An EC2-backed site is unreachable

**Start with** the affected URL, instance ID, Region, deployment window and, if applicable, target-group ARN. Set and verify the account using the [AWS cheat sheet](README.md). All commands below are read-only.

1. **Identify the instance and health dimensions.** Include all instance states so a stopped instance is visible.

   ```bash
   instance_id=i-0123456789abcdef0
   aws ec2 describe-instance-status --instance-ids "$instance_id" --include-all-instances \
     --query 'InstanceStatuses[].{ID:InstanceId,State:InstanceState.Name,System:SystemStatus.Status,Guest:InstanceStatus.Status,EBS:AttachedEbsStatus.Status}' --output json
   ```

   | Observation | Next step |
   | --- | --- |
   | System status impaired | Check AWS Health and scheduled events. Give the infrastructure owner the instance ID, AZ and timestamp. Use the workload’s approved failover procedure if impact persists. |
   | Instance/guest status impaired | Inspect guest boot, filesystem, memory and network logs through existing management access. |
   | Attached EBS impaired on a supported instance | Inspect volume health and I/O metrics, then involve the storage owner. A missing field can reflect platform or CLI support. |
   | Initializing, stopped, empty response or invalid ID | Confirm intended state and Region, wait for a fresh status sample or correct the identifier. |
   | All applicable checks pass | Move up to the load balancer, listener and application. |

2. **If a load balancer is in the path**, inspect the exact target and port. Omit this step for a directly served instance.

   ```bash
   target_group_arn='arn:aws:elasticloadbalancing:us-east-1:111122223333:targetgroup/example/0123456789abcdef'
   aws elbv2 describe-target-health --target-group-arn "$target_group_arn" \
     --query 'TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,State:TargetHealth.State,Reason:TargetHealth.Reason,Detail:TargetHealth.Description}' --output json
   ```

   A response-code mismatch points toward the configured health path, matcher, redirects or vhost. A timeout calls for listener, security group path, target capacity and app latency checks. Match the probe’s protocol, port and host behaviour.
3. **Check the same request at the next boundary.** Using the existing host management path, inspect `ss -lnt` and the service journal. Compare a known safe application request locally and through the public hostname. A healthy target with a broken public path directs attention to DNS, frontend TLS or listener rules.
4. **Close with a diagnosis and owner.** Record the first boundary where the response differs, its reason and the affected user path. After an approved fix, confirm target health over its configured threshold and repeat the public request, checking its expected body. Reboot, stop/start and volume replacement need a separate recovery decision because they affect availability and data.

[AWS cheat sheet](README.md) · [EC2 status dimensions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-system-instance-status-check.html) · [Instance status CLI](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instance-status.html) · [Target health CLI](https://docs.aws.amazon.com/cli/latest/reference/elbv2/describe-target-health.html)
