# PWA & Mobile Support

Transcript Tower is installable as a Progressive Web App (PWA) on modern browsers and mobile devices.

- Add to home screen for a native app-like experience
- Works offline for static assets and dashboard
- Responsive Bootstrap 5 UI for all devices

**How it works:**
- `manifest.webmanifest` and `service-worker.js` are in `static/`
- Service worker caches static assets for offline use
- App icon and theme color are set for mobile

**To customize:**
- Update icons in `static/`
- Edit `manifest.webmanifest` for app name, colors, etc.
- Extend `service-worker.js` for advanced offline support

---
