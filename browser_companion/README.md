# SAPIANTA Governed Browser Companion

Minimal local-only browser companion for explicit human-triggered governed
runtime invocation.

## Scope

- one popup action: `Invoke governed runtime`
- one endpoint: `http://127.0.0.1:8110/governed-invoke`
- one explicit artifact input
- no page scraping, no credential access, no automatic prompt submission

## Manual Test

1. Start the local preview runtime:

   ```bash
   cd ~/work/sapianta/sapianta_system
   python
   from runtime.preview.governed_local_preview_runtime import create_local_preview_server
   server = create_local_preview_server(host="127.0.0.1", port=8110)
   server.serve_forever()
   ```

2. Load the extension:
   - open `chrome://extensions`
   - enable Developer mode
   - choose `Load unpacked`
   - select `browser_companion/`

3. Open ChatGPT in the browser.
4. Click the SAPIANTA companion extension.
5. Choose `Natural Language Intent`.
6. Enter:

   ```text
   create governance artifact for operational replay proof
   ```

7. Click `Preview intent`.
8. Inspect the interpreted preview and click `Confirm preview`.
9. Click `Invoke governed runtime`.

Expected result:

```text
status: RETURNED
closure: PASS
replay evidence visible
```
