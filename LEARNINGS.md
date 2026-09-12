# Learnings — 2.0 process + metrics dashboard

## What 1.0 taught

The ponytail table was a valid assignment surface and a poor decision surface.
A scheduler does not open the tool to "see a grid." They open it to answer:
**can we generate today’s go, and if not, what is the next gap?**

A table of dropdowns hid that question. Demo stages 01–06 already encoded a process,
but the UI never named the process or measured progress through it.

## Design choices

**Chose derived process stages over a new status enum.**
Alternative: replace `planned / crew-ready / airborne` with six stored states.
Reason: keep demo stages and existing assignment APIs intact; stage is insight.
Revisit: production state machine with legal transitions (bead P2).

**Chose decision-first hierarchy over more chrome.**
Alternative: kanban columns for each process step.
Reason: four-ship day still fits one board; funnel + exceptions give the process
without splitting the schedule across six lists.
Revisit: if the unit flies 16+ lines, split the board by stage.

**Primary metric is executable %**, not sorties planned.
Supporting metrics: tails, loadouts, crew fill, airborne.
Exceptions list is the action queue (IxDF: highlight exceptions, not averages).

## What failed / was discarded

- Putting metrics only in the README. They have to live in the product.
- Treating "crew-ready" as the only process signal. Most of the work happens
  before status ever changes: tail → loadout → crew.
- Pure ponytail compression. It removed the language the user needed
  (process, funnel, next action).
