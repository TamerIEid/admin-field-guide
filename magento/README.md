# Magento daily cheat sheet

For Magento Open Source and Adobe Commerce 2.4 installations that provide `bin/magento`. Run from the deployed release root as the application filesystem owner. Managed cloud platforms may provide their own deployment, logging and scheduler controls. Use the platform owner’s workflow there.

| Question | First check | How to interpret it |
| --- | --- | --- |
| Am I in the live release? | `pwd -P`, `bin/magento --version` and `bin/magento deploy:mode:show` | Compare the resolved path, version and mode with the deployment record. |
| Should this node serve traffic? | `bin/magento maintenance:status` | An enabled flag during an active release can be intentional. Test as an ordinary visitor, since an exempt address can still see the store. |
| Why is one price old? | `bin/magento indexer:status catalog_product_price` and `bin/magento indexer:show-mode catalog_product_price` | Check status, schedule age and backlog together. Match website, currency, quantity and customer group. |
| Which caches are enabled? | `bin/magento cache:status` | The output shows enabled types. An enabled type alone says nothing about the age of a particular URL. |
| Are jobs progressing? | `tail -n 60 var/log/cron.log`, if file logging is configured | Compare timestamps with the active scheduler and recent rows in `cron_schedule`. A future pending job is expected. |
| Which exception matches this failure? | `tail -n 60 var/log/exception.log` on the affected node | Correlate the first exception with the request time, release and any report ID. Redact request data from handoffs. |
| Is the data current on the storefront? | Open one known product in its intended store view | Compare the anonymous product and category prices with the expected effective price. A healthy home page misses this failure. |

**Cache clean and flush have different scopes.** A type-specific clean through Commerce invalidates entries for that type. Flushing backend storage can evict entries used by other applications. Identify the layer and the affected type before any eviction.

[Wrong price](stale-price.md) · [Late jobs](cron-backlog.md) · [Maintenance 503](maintenance-503.md) · [Adobe cache management](https://experienceleague.adobe.com/en/docs/commerce-operations/configuration-guide/cli/manage-cache) · [Adobe indexer commands](https://experienceleague.adobe.com/en/docs/commerce-operations/configuration-guide/cli/manage-indexers)
