# Learnings — 2.1 aircraft scheduling

## What 2.0 taught

Decision-first metrics answer “can we generate today’s go?” but treated
aircraft as a label on a sortie, not a scarce time-bound asset.

## What 2.1 taught

**Aircraft scheduling is window + role, not same-day uniqueness.**
Same-calendar-day locks are too coarse. Primary consumes a takeoff→land
window plus turn buffer; a ground spare may cover many lines.

**Spare is go-risk language, not optional chrome.**
Missing spare stays an exception pressure; it does not hard-block
crew-ready (unlike ER, crew, loadout, config).

**Crew-ready without ER is a lie on the desk.**
Executable % must not climb until release is signed.

**Pen-and-ink is the trust surface.**
Replace/upsert without a change log trains people to distrust the board.

## Design choices

**Derived stages stay.** Still insight, not a stored state machine (P2).

**Config mismatch is a hard blocker.** Wrong jet for the weapons template
cannot be marked crew-ready.

**Inclusive turn buffer.** Next takeoff must be after land + buffer
(touching times conflict).

## Spec / beads

OpenSpec is now capability specs + `features/*.feature`. Beads (`bd`)
tracks A1–A13 (closed on this branch) and production P1–P6.
