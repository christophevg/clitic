# Framework Risk Assessment: Textual

**Date:** 2026-04-20
**Status:** Ongoing Monitoring

---

## Assessment

Keep a close eye on Textual — avoid spinning down rabbit hole that doesn't produce what's needed.

## Key Questions

1. **What triggers abandoning Textual?**
   - API instability (frequent breaking changes)
   - Performance issues at scale
   - Missing critical features
   - Maintenance concerns
   - License changes

2. **What alternatives exist?**
   - **Rich**: Already a dependency for rendering, but limited TUI capabilities
   - **Textual forks**: Community-maintained versions if upstream slows
   - **Custom widget framework**: Build on Rich directly (high effort)
   - **Alternative TUI frameworks**: urwid, npyscreen (different paradigms)
   - **Terminal-only mode**: Drop TUI, focus on output formatting

## Current Status

- Textual version: 0.50.0+ (pinned in pyproject.toml)
- API used: Widget, App, ScrollView, TextArea, reactive properties
- Custom abstractions: ContentPlugin, CompletionProvider, ModeProvider
- Risk level: **Low** (good abstractions in place)

## Monitoring Criteria

| Indicator | Current | Concern Threshold |
|-----------|---------|-------------------|
| Breaking changes per release | TBD | >2 per minor version |
| Issue response time | TBD | >30 days |
| Release frequency | TBD | <1 per quarter |
| Performance regressions | TBD | >20% slowdown |

## Mitigation Strategy

The plugin abstraction layer (ContentPlugin, CompletionProvider, ModeProvider) provides insulation from Textual API changes. If Textual becomes problematic:

1. **Phase 1**: Pin version, document limitations
2. **Phase 2**: Fork and maintain critical fixes locally
3. **Phase 3**: Abstract Textual behind internal interfaces, evaluate alternatives
4. **Phase 4**: Migrate to alternative framework

## Action Items

- [ ] Monitor Textual changelog for breaking changes
- [ ] Review quarterly for API stability
- [ ] Document any workarounds for Textual limitations