# Journal Scope Recheck

Date: 2026-04-18

This note rechecks the most likely target journals using their current official pages rather than older internal assumptions.

## 1. Sensors

Official source:

- https://www.mdpi.com/journal/sensors/about

What the current official scope says:

- `Sensors` positions itself as a forum for sensor science, sensor applications, signal processing and data fusion in sensor systems, sensors and robotics, and multi-sensor positioning and navigation.
- The page also explicitly says full experimental details should be provided so results can be reproduced.

Why this matches the current manuscript:

- Our paper is fundamentally about uncertain bearing measurements.
- The method is a sensing / localization / estimation framework rather than a pure UAV mission paper.
- The project already has a reproducibility-oriented package, which aligns with the journal's stated emphasis.

Current judgment:

- `Best overall fit`.

## 2. Drones

Official sources:

- https://www.mdpi.com/journal/drones/about
- https://www.mdpi.com/journal/drones/instructions

What the current official scope says:

- `Drones` focuses on the design and applications of drones and specifically lists onboard sensors, signal/image processing, navigation and position/orientation, GNSS outages, autonomy, and mission planning.
- The journal also states a special requirement: the manuscript must clearly and directly address unmanned platforms.
- The instructions emphasize reproducibility, full datasets where possible, and a standard article structure including Highlights and the usual Methods / Results / Discussion sections.
- The graphical-abstract guidance is explicit, and the figure-format section currently prefers figures at no less than 600 dpi.

Why this matches the current manuscript:

- The application framing is explicitly collaborative UAV sensing under GNSS-denied conditions.
- The paper already contains UAV language, bearing-only sensing, and GNSS-denied mission motivation.

What still limits the fit slightly:

- The evidence is simulation-based rather than platform-validated.
- `Drones` is a stronger fit when the UAV-platform context is foregrounded more strongly than the generic sensing contribution.

Current judgment:

- `Very good fit`, especially if the UAV application framing is emphasized.

## 3. Scientific Reports

Official source:

- https://www.nature.com/srep/about

What the current official scope says:

- `Scientific Reports` is broad and welcomes work from the natural sciences, medicine, and engineering.
- The journal describes itself as looking for scientifically robust and original work with broad discoverability.

Why the current manuscript is less naturally matched:

- The paper is solid and coherent, but still simulation-based.
- The current novelty is practical and moderate, not obviously broad-impact engineering in the `Scientific Reports` sense.
- The paper becomes more realistic for this route after stronger validation, broader systems integration, or richer uncertainty quantification.

Current judgment:

- `Stretch target`, not the safest first submission.

## 4. Practical Recommendation

Current order:

1. `Sensors`
2. `Drones`
3. `Scientific Reports`

Reason:

- `Sensors` is the best science-scope match.
- `Drones` is the best application-scope match.
- `Scientific Reports` is broader but would benefit from another strengthening round.

## 5. Format Reminder

- The current package is already in MDPI LaTeX format.
- Current figures are exported at 300 DPI, which satisfies the user's requested high-resolution baseline.
- If the first target is `Drones`, rerender the figures and graphical abstract at 600 DPI before final portal upload to align with the current official preference.
