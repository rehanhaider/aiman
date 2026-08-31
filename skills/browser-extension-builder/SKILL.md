---
name: browser-extension-builder
description: Use when building browser extensions - Chrome, Firefox, or cross-browser. Covers Manifest V3 architecture, content scripts, service workers, popup and side panel UIs, permissions strategy, storage, messaging, monetization, and Chrome Web Store publishing.
license: Apache-2.0
source: adapted from vibeship-spawner-skills (Apache 2.0)
metadata:
  version: "2.0.0"
  domain: browser-extensions
  triggers: browser extension, chrome extension, firefox addon, manifest v3, content script, service worker extension, web store
  role: architect
  scope: implementation
  output-format: code
---

# Browser Extension Builder

Build Manifest V3 extensions that pass store review and survive the service-worker lifecycle. The three most common failure modes in extension code are: treating the service worker as a persistent background page, using callback-style APIs where MV3 is promise-based, and requesting broader permissions than the store will approve.

## Core Workflow

1. **Scope the surfaces** — Which of popup, side panel, content script, options page, and service worker does this feature actually need? Fewer surfaces = less review friction.
2. **Design the permission set** — Start from `activeTab` + `storage`; add specific `host_permissions` only for hosts you must touch without a user gesture. Broad permissions (`<all_urls>`, `tabs`, `webRequest`) trigger manual store review and user-facing warnings.
3. **Build with the message flow drawn first** — Popup/side panel ←→ service worker ←→ content script, with `chrome.storage` as shared state. Write the flow down before coding; retrofitting messaging is painful.
4. **Test the lifecycle** — Kill the service worker (chrome://serviceworker-internals or just wait 30s) and confirm the extension still works. Reload a tab and confirm content scripts re-inject.
5. **Prepare for review** — Single-purpose description, minimal permissions with justifications, privacy policy if you touch user data.

## Architecture

### Project structure

```
extension/
├── manifest.json
├── popup/           # click-the-icon UI (short-lived)
├── sidepanel/       # persistent per-tab UI (Chrome 114+), better for tools users keep open
├── content/         # runs in the page; isolated world, shared DOM
├── background/      # service worker: event router, NOT a long-lived process
├── options/         # settings page
└── icons/           # 16 / 48 / 128 px
```

### Manifest V3 template

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "One sentence, one purpose — store reviewers reject multi-purpose descriptions.",
  "permissions": ["storage", "activeTab", "scripting"],
  "host_permissions": ["https://specific-site.com/*"],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": { "16": "icons/icon16.png", "48": "icons/icon48.png", "128": "icons/icon128.png" }
  },
  "background": { "service_worker": "background/service-worker.js", "type": "module" },
  "content_scripts": [{
    "matches": ["https://specific-site.com/*"],
    "js": ["content/content.js"],
    "run_at": "document_idle"
  }],
  "options_page": "options/options.html"
}
```

Never ship `"matches": ["<all_urls>"]` unless the extension genuinely operates on every site (and be ready to justify it in review). For features that act on the current tab after a click, prefer `activeTab` + programmatic injection:

```javascript
// service worker — inject only when the user asks, no host_permissions needed
chrome.action.onClicked.addListener(async (tab) => {
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["content/content.js"],
  });
});
```

## Service worker rules (where extensions break)

The MV3 service worker is **event-driven and ephemeral**: Chrome kills it after ~30s of inactivity and restarts it on the next event.

- **No global state.** Anything you need later goes in `chrome.storage` (`session` for in-memory-equivalent state, `local` for persistent).
- **No `setTimeout`/`setInterval` for anything > 30s.** Use `chrome.alarms` — timers die with the worker.
- **Register all event listeners synchronously at the top level.** Listeners registered inside async callbacks are lost when the worker restarts.
- **Don't fight the lifecycle with keep-alive hacks.** Design stateless handlers instead.

```javascript
// background/service-worker.js
chrome.alarms.create("sync", { periodInMinutes: 15 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "sync") return;
  const { token } = await chrome.storage.local.get("token");
  // ... fetch and store
});
```

## Content scripts

Content scripts run in an **isolated world**: they share the page's DOM but not its JavaScript variables. `run_at: document_idle` (the default) fires **after** DOM ready — do not wrap startup logic in a `DOMContentLoaded` listener, it may never fire because the event already happened.

```javascript
// content/content.js — at document_idle the DOM is already available
const element = document.querySelector(".target");
element?.classList.add("my-extension-highlight");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "getData") {
    sendResponse({ data: document.querySelector(".data")?.textContent });
    return; // responded synchronously — do NOT return true here
  }
  if (message.action === "getDataAsync") {
    fetchSomething().then((data) => sendResponse({ data }));
    return true; // return true ONLY when sendResponse is called later/async
  }
});
```

Inject UI with a unique id/class prefix and explicit `z-index`; prefer a closed `ShadowRoot` so page CSS can't restyle your UI (and yours can't leak into the page):

```javascript
const host = document.createElement("div");
host.id = "my-extension-root";
const shadow = host.attachShadow({ mode: "closed" });
shadow.innerHTML = `<style>.panel{position:fixed;bottom:20px;right:20px;z-index:2147483647}</style>
  <div class="panel"><button id="go">Run</button></div>`;
shadow.getElementById("go").addEventListener("click", run);
document.documentElement.append(host);
```

## Storage and messaging

All `chrome.*` APIs return promises in MV3 — use `async/await` directly, never hand-rolled promise wrappers or callbacks.

```javascript
await chrome.storage.local.set({ settings: { theme: "dark" } });
const { settings } = await chrome.storage.local.get("settings");

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.settings) applyTheme(changes.settings.newValue);
});
```

| Area      | Limit                       | Use for                                          |
| --------- | --------------------------- | ------------------------------------------------ |
| `local`   | 10 MB (5 MB before Chr 114) | User data, caches                                |
| `sync`    | 100 KB total, 8 KB/item     | Settings that follow the user across devices     |
| `session` | 10 MB, in-memory            | Service-worker state that must survive restarts  |

## Cross-browser support

- Firefox and Safari support MV3; Firefox also still runs MV2 and uses `browser.*` (promise-based) with `chrome.*` compatibility. Target `chrome.*` promises and the differences are small.
- Firefox requires `browser_specific_settings.gecko.id` in the manifest and uses `background.scripts` (event pages) rather than service workers — keep background logic stateless and the same code runs on both.
- Use [webextension-polyfill](https://github.com/mozilla/webextension-polyfill) only if you must support MV2 Firefox; otherwise plain `chrome.*` promises suffice.

## Monetization (brief)

Chrome Web Store has no built-in payments. The workable pattern: license check against your own backend.

1. "Upgrade" button opens `https://your-site.com/upgrade?ext_user=<id>` in a new tab (checkout lives on the web, not in the extension).
2. After payment, the extension polls your API for entitlement and caches it: `await chrome.storage.local.set({ isPremium })`.
3. Gate features on the cached flag; re-verify server-side for anything abusable.

Models that fit extensions: freemium (most common), one-time unlock, or donations for personal tools. Don't build subscription infrastructure before the free tier has retention.

## Constraints

### MUST DO
- Use promise-based `chrome.*` APIs with async/await (MV3 supports promises everywhere)
- Keep the service worker stateless; persist via `chrome.storage`, schedule via `chrome.alarms`
- Register event listeners synchronously at the worker's top level
- Scope `matches`/`host_permissions` to the narrowest host set that works
- Namespace or shadow-DOM all injected UI (page CSS collisions are the #1 injected-UI bug)
- Test with the service worker killed and the extension reloaded mid-session
- Provide 16/48/128 px icons and a single-purpose store description

### MUST NOT DO
- Wrap content-script startup in `DOMContentLoaded` when `run_at` is `document_idle` (the event has already fired)
- `return true` from `onMessage` handlers that respond synchronously (it leaks the message channel)
- Use `setTimeout`/`setInterval` in the service worker for anything beyond seconds
- Request `<all_urls>` or `tabs` "to be safe" — every broad permission is store-review friction and a scarier install prompt
- Fetch remote code (banned in MV3 — all executed JS must ship in the package)
- Store secrets in the extension; anyone can unzip a CRX

## Validation checks

| Check                                                | Severity | Fix                                                     |
| ---------------------------------------------------- | -------- | ------------------------------------------------------- |
| Manifest V2 anywhere                                  | HIGH     | Migrate: service worker, `action`, `host_permissions`   |
| `<all_urls>` or unused permissions in manifest        | HIGH     | Narrow `matches`; move one-shot access to `activeTab`   |
| Global state or long timers in service worker         | HIGH     | `chrome.storage.session` + `chrome.alarms`              |
| Callback-style `chrome.*` with hand-rolled wrappers   | MEDIUM   | Use the native promise forms                            |
| Injected UI without namespace/shadow root             | MEDIUM   | Shadow DOM host element with unique id                  |
| Missing icons or multi-purpose description            | LOW      | 16/48/128 icons; one-sentence single purpose            |

## Related Skills

- `react-expert` — when the popup/side panel UI grows beyond vanilla JS
- `ux-copy` — store listing copy, permission-prompt explanations, onboarding text
