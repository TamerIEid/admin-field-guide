# One product shows the wrong price

**Before changing anything**, identify a SKU, website/store view, currency, customer group, quantity and expected effective price. Check active catalog rules, special-price dates, tax display and currency conversion with the merchant. Use the same visitor context for every comparison.

1. **Reproduce the discrepancy.** Record the expected amount and the amounts on the product and category pages. Check an anonymous browser session. If you have an approved origin-check path, compare it with the public response. A different store view, cookie or cache key can give a legitimate difference.
2. **Inspect only the price index first.** Run as the filesystem owner from the active release.

   ```bash
   bin/magento indexer:show-mode catalog_product_price
   bin/magento indexer:status catalog_product_price
   ```

   In scheduled mode, sample status twice across two normal scheduler intervals. A shrinking backlog suggests work in progress. A backlog that grows while successful index jobs disappear points to the scheduler. If indexing is already running, let it finish or investigate the owning job before starting more work.

3. **Select the matching branch.**

   | Finding | Next action |
   | --- | --- |
   | Expected source price is wrong for this website/group | Give the SKU, scope and price calculation to merchandising. Obtain a corrected source value before reindexing. |
   | Scheduled work has stopped | Follow the [cron backlog runbook](cron-backlog.md). Confirm new scheduled work completes. |
   | Correct source, invalid price index, capacity available, and no index run in progress | In an approved low-load window on a CLI-indexed installation, run `bin/magento indexer:reindex catalog_product_price` once. This can process many SKUs. |
   | Origin shows the right amount and the edge serves the old one | Inspect the full-page cache and CDN policy for the affected public page. Use the store’s supported invalidation flow. |

   A store using a SaaS price index needs its service-specific feed status. A local index rebuild cannot establish that feed’s freshness.

4. **Verify the amount users see.** Fetch the same SKU in the same context and confirm both storefront amounts. Check a second SKU as a control, rerun indexer status and record elapsed time. If the price remains wrong with a healthy index, hand off the observed source, computed amount and cache evidence. Repeating a full reindex can consume capacity during trading.

[Magento cheat sheet](README.md) · [Adobe index modes and reindexing](https://experienceleague.adobe.com/en/docs/commerce-operations/configuration-guide/cli/manage-indexers)
