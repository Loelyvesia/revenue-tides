# Performance and build audit

Production build: PASS (`vite build`, ES2022 target, no source maps).

| Asset | Uncompressed | Gzip |
| --- | ---: | ---: |
| `dist/assets/index-*.js` | 107.29 KB | 40.27 KB |
| `dist/assets/index-*.css` | 26.78 KB | 5.71 KB |
| `dist/index.html` | 0.91 KB | 0.56 KB |
| Phase G public web data | 182.03 KB | not precompressed |

The application has one runtime dependency, Vue. It includes no chart library, UI suite, router, state manager, font bundle, image/video asset, animation framework, backend, telemetry, or source map. Series details and the source registry are deferred. The main authored application bundle plus CSS is approximately 134 KB uncompressed and comfortably below the project’s performance envelope.

Local installation initially encountered npm registry `ETIMEDOUT`; verification used a local copy of an already installed matching Vue/Vite toolchain, never a link into or write to Project 01. `package-lock.json` was generated offline from the resolved local dependency tree. Future clean environments can use the normal lockfile when registry access is available.
