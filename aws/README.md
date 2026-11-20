# AWS daily cheat sheet

For AWS CLI v2 with an authorized, read-only role. Every task starts by checking account and Region. An empty result can mean the wrong Region, filter or resource identifier. AccessDenied means the inventory is incomplete.

```bash
export AWS_PROFILE=ops-readonly
export AWS_REGION=us-east-1
export AWS_PAGER=""
aws sts get-caller-identity --query '{Account:Account,Role:Arn}' --output json
```

Use your own profile and Region. Compare the returned account and role with the workload inventory. Keep account identifiers and resource names in the private incident record.

| Shift question | First place to check | Decision |
| --- | --- | --- |
| Can customers use the service? | Known public health or user path, then EC2 status checks and target-group health | A passing hypervisor check still leaves the application path to test. |
| Which alerts are firing or missing data? | CloudWatch → Alarms, filter on `ALARM` and then `INSUFFICIENT_DATA` | Open the alarm’s state reason, evaluation window and history. Compare with the metric and traffic at the same time. |
| Did a notification reach a person? | Alarm history → action entry, then subscription, delivery or recipient evidence | Record state change, service action, delivery and acknowledgement separately. |
| How recent is a recoverable copy? | AWS Backup → vault → matching resource and recovery point | Compare capture time with the workload’s recovery point objective. Locate the latest tested restore. |
| Is today’s spend unusual? | Billing → Cost Explorer, daily granularity, group by Service; check the billing period and account scope | Compare recent **complete** days on the same cost basis. Current-period costs can arrive late. Follow up a changed service by account, Region and usage type. Billing access is separate. |
| What changed just before the incident? | CloudTrail → Event history in the affected Region | Search the resource/actor and UTC window for relevant management events. Service and data-plane logs may also be needed. |

[EC2 reachability](ec2-unreachable.md) · [CloudWatch alarm history](alarm-history.md) · [AWS Backup freshness](backup-freshness.md) · [STS caller identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html) · [Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html) · [CloudTrail event history](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html)
