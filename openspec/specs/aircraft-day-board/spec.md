# Aircraft Day Board

## Purpose

Give the desk an asset-centric view: for each jet, status, configuration, and
the sorties it supports today as primary or spare.

## Requirements

### Requirement: Aircraft schedule endpoint

The system SHALL expose an aircraft day schedule derived from sorties.

#### Scenario: View aircraft day board

- **GIVEN** tails are assigned on one or more sorties
- **WHEN** I request the aircraft schedule for the day
- **THEN** each aircraft lists its status, config, and timed commitments
  (primary and spare) with takeoff and land
- **AND** unassigned MC/PMC jets appear with an empty commitment list
