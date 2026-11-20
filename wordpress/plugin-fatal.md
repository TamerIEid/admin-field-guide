# Recover from a fatal error after a plugin change

**Start with evidence.** A generic “critical error” page gives little detail. Capture one failing URL, a UTC timestamp and the first fatal PHP exception for that request. Confirm the implicated plugin path and recent change in the deployment record. A plugin named at the end of a stack trace can be the caller of a fault elsewhere.

1. **Find the target even when normal bootstrap fails.** From the site root, select the confirmed plugin slug. The following commands skip ordinary plugins and the theme during this CLI invocation. Must-use plugins still load.

   ```bash
   plugin=example-plugin
   wp --skip-plugins --skip-themes option get home
   wp --skip-plugins --skip-themes plugin get "$plugin" --fields=name,status,version
   ```

2. **Choose the recovery that keeps site data consistent.** On a deployed or managed install, prefer the previous known-good artifact through its release mechanism. On a writable single-site install, if the owner accepts losing this plugin’s functionality temporarily and the plugin can be disabled safely, deactivate only the implicated slug. Payment, authentication, security or order-processing plugins may need traffic controls and a coordinated rollback first.

   ```bash
   wp --skip-plugins --skip-themes plugin deactivate "$plugin"
   wp --skip-plugins --skip-themes plugin get "$plugin" --fields=name,status,version
   ```

   Skipping plugins during this operation can bypass their deactivation hooks. Reconcile any scheduled jobs or vendor cleanup through the plugin owner. If the CLI still fails with plugins skipped, inspect must-use plugins, drop-ins, PHP and the first fatal before widening the change.

3. **Test like the affected user.** Open the original path anonymously, check a recognizable body, then sign into the admin screen if that was affected. Correlate a new request with the PHP log. Verify the feature supplied by the disabled plugin and record any service limitation.
4. **Return the feature.** In staging, install the known compatible version and use the [single-plugin rehearsal](update-plugin.md). Confirm any database changes are compatible before restoring the plugin. Reactivate the tested build through the usual release path and check both the original route and the feature itself. Hand over the old/new versions and the first clean request time.

[WordPress cheat sheet](README.md) · [WP-CLI deactivation and global flags](https://developer.wordpress.org/cli/commands/plugin/deactivate/) · [WordPress debugging](https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/)
