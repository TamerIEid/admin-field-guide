# Practice a WordPress plugin rollback

Use a **disposable, single-site WordPress install**, a shell with WP-CLI and Python 3, and permission to add a plugin and a post. The small plugin registers one shortcode. Two local versions display different text, so a reader can tell which version the site actually serves.

1. From the **guide repository root**, generate the two ZIPs in a fresh temporary directory. Keep the same shell for all steps.

   ```bash
   packages=$(python3 wordpress/practice/make-fixtures.py)
   ls "$packages"
   ```

2. Change directory to your **disposable WordPress root**. Confirm the site address. Check that the practice plugin name is unused with `wp plugin list --field=name`, then install version 1 and create one sample post.

   ```bash
   wp option get home
   wp plugin install "$packages/field-guide-practice-1.0.0.zip" --activate
   post_id=$(wp post create --post_type=post --post_title='Field guide practice' \
     --post_status=publish --post_content='[field_guide_marker]' --porcelain)
   wp post url "$post_id"
   ```

3. Open the printed URL. Expect `field-guide-1.0.0` in the article. Install version 2 over the existing plugin and inspect its status. Reload that same post through an uncached staging path.

   ```bash
   wp plugin install "$packages/field-guide-practice-2.0.0.zip" --force
   wp plugin get field-guide-practice --fields=name,status,version
   ```

   Expect status `active`, version `2.0.0` and the visible text `field-guide-2.0.0`. If the admin reports version 2 while the article still shows version 1, check which layer cached the public response.

4. Apply the previous package and read the post again. Pass when the plugin remains active and the same URL once again displays `field-guide-1.0.0`.

   ```bash
   wp plugin install "$packages/field-guide-practice-1.0.0.zip" --force
   wp plugin get field-guide-practice --fields=name,status,version
   wp post url "$post_id"
   ```

5. When finished, trash the sample post and remove the practice plugin from this disposable installation.

   ```bash
   wp post delete "$post_id"
   wp plugin deactivate field-guide-practice
   wp plugin delete field-guide-practice
   ```

[WordPress cheat sheet](../README.md) · [Use this rehearsal on a real release](../update-plugin.md)
