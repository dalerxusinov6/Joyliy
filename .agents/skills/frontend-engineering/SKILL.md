---
name: frontend-engineering
description: Build maintainable, responsive, accessible frontend interfaces using the project's existing framework and conventions.
---

# Frontend Engineering

Use when implementing or refactoring frontend pages, components, layouts, forms, or responsive behavior.

## Rules
1. Inspect the available project files and follow the existing architecture before proposing changes.
2. Prefer the project's installed framework, libraries, naming conventions, and styling approach. Do not migrate frameworks without explicit approval.
3. Build reusable components where reuse improves clarity; avoid premature abstraction.
4. Keep components focused and state predictable. Handle loading, empty, success, and error states where relevant.
5. Use semantic HTML, accessible labels, keyboard navigation, focus visibility, and suitable ARIA only when needed.
6. Make layouts responsive with flexible sizing and sensible breakpoints. Test narrow screens conceptually and avoid horizontal overflow.
7. Use optimized assets and avoid unnecessary dependencies, large client bundles, and avoidable re-renders.
8. Validate forms and user input. Never expose secrets, API keys, or private credentials in client code.
9. Do not claim tests or builds passed unless they were actually run. If tools are unavailable, provide the exact checks the user should run.
10. Keep changes scoped to the request and explain important trade-offs.

## Preferred finish
Summarize files or areas changed, explain how to run the project, and list validation performed or still needed.
