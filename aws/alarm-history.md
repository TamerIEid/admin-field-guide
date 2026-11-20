# A CloudWatch alarm fired and nobody saw a page

**Scope.** Diagnose one metric alarm and its existing action. Use the verified profile and Region from the [AWS cheat sheet](README.md). Collect the incident’s UTC window and intended notification destination. These reads do not generate a test notification.

1. **Inspect the alarm’s evaluation and wiring.** Set the exact case-sensitive alarm name.

   ```bash
   alarm=example-high-cpu
   aws cloudwatch describe-alarms --alarm-names "$alarm" \
     --query 'MetricAlarms[].{Name:AlarmName,State:StateValue,Reason:StateReason,Period:Period,Periods:EvaluationPeriods,Required:DatapointsToAlarm,Missing:TreatMissingData,Enabled:ActionsEnabled,OnAlarm:AlarmActions,OnOK:OKActions}' --output json
   ```

   Compare the metric dimensions, statistic and threshold in the console with the actual workload. For metric math inspect each expression and period. An empty result also warrants checking whether the named alarm is composite.
2. **Read events on both sides of the expected transition.** Replace the dates with the incident window. Look for StateUpdate, Action and ConfigurationUpdate rows.

   ```bash
   start_utc=2026-01-15T08:00:00Z
   end_utc=2026-01-15T09:00:00Z
   aws cloudwatch describe-alarm-history --alarm-name "$alarm" \
     --start-date "$start_utc" --end-date "$end_utc" --scan-by TimestampAscending \
     --query 'AlarmHistoryItems[].{UTC:Timestamp,Kind:HistoryItemType,Detail:HistorySummary}' --output json
   ```

3. **Find the first missing step.**

   | Evidence | Interpretation and action |
   | --- | --- |
   | No transition into ALARM in the window | Check metric timestamps, missing-data treatment and M-of-N evaluation. A standard SNS alarm action usually runs on transition. An alarm already in ALARM may stay there. |
   | Transition but no expected action | Check whether actions were enabled at the time and the configured destination for that state. Inspect configuration history. |
   | Action entry reports failure | Read that entry’s error and route it to the topic policy, KMS or target owner as appropriate. |
   | Action succeeded, recipient saw nothing | Check the exact SNS subscription is confirmed, any filtering or downstream integration and destination-specific delivery evidence. Success invoking SNS does not establish inbox receipt. |

4. **Record the outcome in order.** Capture the metric window, state transition, action result, recipient evidence and acknowledgement time. Mark the first missing item and assign its owner. If a routing fix needs an end-to-end test, use an agreed test alarm and destination and record a fresh transition and actual receipt.

[AWS cheat sheet](README.md) · [CloudWatch alarm behaviour](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html) · [Alarm configuration CLI](https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/describe-alarms.html) · [Alarm history CLI](https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/describe-alarm-history.html)
