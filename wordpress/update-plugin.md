# Rehearse one plugin update and its rollback

To practice the sequence with local packages and a visible version marker, use the [disposable plugin exercise](practice/README.md).

**Environment.** Use an isolated, writable single-site staging copy. Disable outbound mail, payment/webhook delivery and scheduled integrations at the environment boundary. Have a matching file-and-database recovery point, the old package, a trusted new package or exact vendor version, and a test login. Composer-managed sites should change the dependency in source and deploy each revision through their normal pipeline.

1. **Record the baseline.** Pick one plugin and one feature it owns. For a form plugin, load the form, submit a synthetic message into a staging mail sink, and record the confirmation and sink receipt. Capture the admin plugin status too.

   ```bash
   plugin=example-plugin
   wp option get home
   wp plugin get "$plugin" --fields=name,status,version
   ```

2. **Review the target and upgrade notes.** Check support for the web PHP and WordPress versions, database migrations and dependent plugins. For a WordPress.org update, preview available changes with `wp plugin update "$plugin" --dry-run`. Set the version selected for the rehearsal; replace the example value.

   ```bash
   target_version=2.4.1
   wp plugin update "$plugin" --version="$target_version"
   wp plugin get "$plugin" --fields=name,status,version
   ```

   For a vendor ZIP, verify the package source and vendor checksum when available, then use `wp plugin install /path/to/verified-new.zip --force` **instead of** the update command. Recheck activation state after replacement.

3. **Test the actual feature.** Repeat the same fixture and confirm a fresh result, expected version, prior activation state, working admin screen and clean PHP log for the request. A “success” message from WP-CLI only proves package handling.
4. **Rehearse rollback on staging.** For a code-only change with confirmed backward-compatible data, replace the plugin with the saved old artifact via `wp plugin install /path/to/verified-old.zip --force`. Restore its baseline activation state and repeat the feature test. When the update migrates data incompatibly, restore the paired pre-update files and database into an isolated copy. Restoring an old live database can discard newer orders or submissions.
5. **Record the release decision.** Capture both version numbers, tested feature, timings and rollback result. A failed forward or rollback test keeps the release in staging. A passing rehearsal gives the release owner an exact version, a test and a recovery procedure.

[WordPress cheat sheet](README.md) · [WP-CLI update](https://developer.wordpress.org/cli/commands/plugin/update/) · [Install a plugin ZIP](https://developer.wordpress.org/cli/commands/plugin/install/)
