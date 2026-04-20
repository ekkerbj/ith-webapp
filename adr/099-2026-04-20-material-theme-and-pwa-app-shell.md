# ADR 099: Material Theme and PWA App Shell

## Metadata
- **Date**: 2026-04-20
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-099 site theme refresh, responsive browser shell, light PWA affordance, brand alignment
- **Tags**: ui, theme, pwa, responsive-design, Flask, css

## Decision
Adopt a Material-inspired shared app shell with a branded header, responsive navigation, stronger surface elevation, and PWA metadata so the site feels consistent on laptop, desktop, and mobile browsers.

## Context
The application already had a shared stylesheet, but the visual system was still closer to a plain line-of-business layout than a modern product UI. The backlog now calls for a clearer brand presentation and a more app-like experience without introducing a frontend framework or JavaScript-heavy shell.

## Alternatives Considered

### Introduce a UI framework
- **Rejected**: would add dependency weight and reduce control over the site-specific brand treatment.

### Leave the existing shell unchanged
- **Rejected**: would preserve the current appearance but would not deliver the requested modern Material-style presentation.

### Build a client-rendered shell
- **Rejected**: unnecessary for the current server-rendered application and would add complexity without a clear user benefit.

## Implementation Details
- Extend `base.html` into a shared app shell with a branded header, primary navigation, skip link, and content surface.
- Add PWA metadata through a manifest link and theme-color meta tag.
- Refresh `src/ith_webapp/static/style.css` with brand colors, elevated surfaces, rounded controls, responsive nav wrapping, and mobile-friendly table behavior.
- Add a lightweight SVG app icon and web manifest so the browser can present the site like an installable app shell.
- Update the inventory reorder dashboard to use the shared base layout instead of a standalone HTML document.

## Validation
- Added regression coverage for the shared shell metadata and layout.
- Verified the theme asset responses and the full pytest suite.
- Full test suite result: 212 passed.

## Consequences
- The UI now reads as a single product rather than a collection of independent pages.
- Mobile and tablet layouts are more usable by default.
- The app remains framework-free, but future pages should follow the shell and CSS token conventions to stay visually consistent.

## Monitoring & Rollback
- **Review date**: 2026-05-04
- **Success metric**: the primary pages share the same shell, remain readable on mobile widths, and present the ITH brand consistently.
- **Rollback strategy**: revert the manifest/icon assets and restore the previous stylesheet if the new shell causes regressions.

## References
- `prd.json` F-099
- `src/ith_webapp/templates/base.html`
- `src/ith_webapp/static/style.css`
- `src/ith_webapp/static/manifest.webmanifest`
- `src/ith_webapp/static/icon.svg`
- `src/ith_webapp/app.py`
- `tests/unit/test_app.py`
- `adr/044-2026-04-19-css-styling-and-responsive-layout.md`
- `adr/043-2026-04-19-navigation-and-switchboard.md`
