# ADR 044: CSS Styling and Responsive Layout

## Metadata
- **Date**: 2026-04-19
- **Status**: Accepted
- **Authors**: The AI
- **Drivers**: F-044 consistent styling, readable line-of-business UI, responsive desktop and tablet layouts
- **Tags**: css, responsive-design, Flask, ui

## Decision
Adopt a shared vanilla CSS stylesheet for the Flask app and have all rendered pages use the common `base.html` shell. Keep the layout framework-free while providing consistent styling for navigation, forms, tables, and mobile/tablet breakpoints.

## Context
The application already renders most views through shared Jinja templates, but it lacked a centralized visual system. The login page was also rendered outside the shared shell, which prevented consistent styling across the app. The backlog calls for a clean, professional, responsive layout without introducing a CSS framework.

## Alternatives Considered

### Use a CSS framework
- **Rejected**: would add dependency and theming overhead for a relatively small application.

### Leave styling to page-specific templates
- **Rejected**: duplicates layout rules and makes consistency harder to maintain.

### Keep the login page standalone
- **Rejected**: breaks the shared visual system and bypasses the common stylesheet.

## Implementation Details
- Keep `base.html` as the shared shell with a global stylesheet link.
- Serve `src/ith_webapp/static/style.css` as the single source of truth for site styling.
- Style navigation, content surfaces, forms, tables, buttons, and links with simple semantic selectors.
- Add responsive media queries so tables stack and spacing tightens on narrower screens.
- Render `/login` through the shared base template so the login form receives the same styling as the rest of the app.

## Validation
- Added tests that assert the login page uses the shared layout and that `/static/style.css` is served with responsive rules.
- Ran the full pytest suite: 102 passed.

## Consequences
- The app now has a consistent look and feel across routes.
- Responsive behavior is handled with a small amount of maintainable CSS.
- The layout remains framework-free, but future page-specific styling should follow the shared stylesheet conventions.

## Monitoring & Rollback
- **Review date**: 2026-05-01
- **Success metric**: all primary pages render through the shared shell and remain usable on tablet-width screens.
- **Rollback strategy**: revert the shared stylesheet or restore page-specific rendering if the common layout causes regressions.

## References
- `prd.json` F-044
- `src/ith_webapp/app.py`
- `src/ith_webapp/templates/base.html`
- `src/ith_webapp/static/style.css`
- `tests/unit/test_app.py`
