# Deadline Replay and Submission Closeout Design

Date: 2026-04-22

## Goal

Strengthen the current `simulation-plus-replay` validation chain with one additional system-facing tier that is still honest about its scope, then close the submission package around that stronger validation story.

## Recommended Approach

Use a `deadline-aware measured-data replay` layer rather than pretending that PX4 SITL or HITL has already been completed.

Why this route:

- it reuses the real geometry, visibility masks, and synchronization structure already available in `data/public_dataset3`;
- it can be executed and reproduced in the current workspace without introducing a heavy autopilot dependency that may not build reliably on the user machine in one pass;
- it directly answers a reviewer-style systems question:
  `if bearings arrive late, become stale, or miss the current front-end cycle, does the robust estimator still help?`

## Validation-Layer Design

1. Start from the existing public multi-view replay cases.
2. For each valid bearing, compute a measured synchronization age from the cross-camera frame mapping.
3. Add link-delay and queue-delay sampling to emulate a cycle-level uplink path.
4. Drop bearings that:
   - miss a front-end deadline;
   - exceed an allowed staleness budget; or
   - are lost by packet-drop sampling.
5. Evaluate the same baseline set on the surviving current-cycle bearings.

This layer is stronger than plain replay because the estimator no longer sees every visible bearing. It must operate with the subset that arrives on time, which is exactly the systems-facing situation the front end is supposed to support.

## Expected Outputs

- new source module for deadline-aware replay filtering;
- new runner script producing a frozen JSON result and case archive;
- one new figure plus one new table;
- manuscript text updates in:
  - Experimental protocol;
  - Results;
  - Discussion / limitations;
- submission-document updates in:
  - `submission/README.md`;
  - `submission/pre_submission_audit.md`;
  - `submission/cover_letter/cover_letter_final.md`;
  - one portal-facing checklist / closeout note.

## Guardrails

- Do not call this full SITL, HITL, HIL, or field deployment.
- Describe it as `deadline-aware measured-data replay` or `companion-loop replay surrogate`.
- Keep the main claim the same:
  robust front-end value is in `upper-tail suppression` and `catastrophic cue reduction`, not universal median dominance.
