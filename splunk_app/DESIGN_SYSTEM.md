# Splunk UI Design System Alignment

This app follows the [Splunk UI Design System](https://splunkui.splunk.com/DesignSystem/Overview) and [accessible color guidance](https://splunkui.splunk.com/DesignSystem/Accessibility/Color).

## Principles applied

| Guideline | Implementation |
|-----------|----------------|
| **Theme tokens** | Dashboards omit `theme="dark"` so Splunk renders light/dark from the user's UI preference (`@splunk/themes`). |
| **WCAG contrast** | Severity and chart colors use Splunk's platform palette (post–9.x A11y refresh), not custom neon hex values. |
| **Color+** | Status fields pair color with text labels (e.g. `🔴 CRITICAL`, `GAP`, `OBSERVED`, `DETECTED`) and patterns (`tactic_bar` blocks). |
| **No color-only instructions** | HTML help panels use headings and lists; links are descriptive text, not color alone. |
| **Functional text** | Custom HTML panels avoid inline `color:` / `background:` — content inherits Splunk theme contrast. |

## Approved palette (Simple XML)

These match Splunk single-value / severity defaults and meet WCAG targets on platform backgrounds:

| Role | Hex | Simple XML |
|------|-----|------------|
| Severe / Critical | `#dc4e41` | `0xdc4e41` |
| High | `#f1813f` | `0xf1813f` |
| Elevated / Medium | `#f8be34` | `0xf8be34` |
| Low / Success | `#53a051` | `0x53a051` |
| Info / Guarded | `#006d9c` | `0x006d9c` |
| Neutral / Gap | `#5c6773` | `0x5c6773` |

## Banned in dashboards

Do not introduce these in new panels (fail `validate_splunk_app.sh`):

- Forced `theme="dark"` on `<dashboard>`
- Custom cyber palette: `#00ff9d`, `#00b4ff`, `#7986cb`, `#546e7a`, `#4fc3f7`, `#81c784`, `#90caf9`
- Inline HTML `style="...color:..."` or `background:#...` on help panels

## Validation

```bash
./scripts/validate_splunk_app.sh
```

Checks XML validity, Cloud vetting rules, and design-system color constraints.
