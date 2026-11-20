# The storefront still returns 503 after a release

**Goal.** Restore traffic only after the active release is ready. You need the release owner, an expected public product URL, and one known-good previous release or a deployment recovery procedure.

1. **Capture the first response.** Record UTC time, route, status and any edge or request ID. Compare the public route with the service’s approved origin health path. A load balancer with no healthy backends can return 503 before Magento sees the request.
2. **Check the serving release as its filesystem owner.**

   ```bash
   pwd -P
   bin/magento maintenance:status
   bin/magento deploy:mode:show
   ```

   Check the deployment system’s status and node list. Read the last step for database upgrade, static content, configuration import or dependency startup. An exempt IP seeing the site while other visitors get 503 is consistent with maintenance mode.

3. **Choose the recovery.** For an unfinished deployment, keep the maintenance window in effect and give the failed step to its owner. If database changes have run, restoring only old code can break compatibility. Use the release’s coordinated code/database recovery plan. If maintenance is already disabled, inspect healthy target count, PHP and application exceptions before changing the flag.
4. **Return the ready release to service.** Use the deployment system’s exit-maintenance action. For a single self-managed node where the flag was left enabled, confirm all release steps completed, health checks pass from the approved preview path and the release owner expects traffic. Then run:

   ```bash
   bin/magento maintenance:disable
   bin/magento maintenance:status
   ```

5. **Verify from a normal visitor address** on the original public product URL. Check status, product content, an asset and a second node or edge location where applicable. If the application starts failing as traffic returns, use the release’s drain or maintenance procedure and alert the owner. Capture both the last working release and the first error after traffic returned.

[Magento cheat sheet](README.md) · [Adobe maintenance mode and exempt addresses](https://experienceleague.adobe.com/en/docs/commerce-operations/installation-guide/tutorials/maintenance-mode)
