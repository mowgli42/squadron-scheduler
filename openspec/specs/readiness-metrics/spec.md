# Readiness Metrics

## Purpose

Answer “can we generate today’s go?” with executable %, process funnel,
exceptions, and aircraft-risk signals (spares, config).

## Requirements

### Requirement: Primary metric

#### Scenario: Readiness metrics answer the primary question

- **GIVEN** the four-ship morning go is on the board
- **WHEN** I view the dashboard
- **THEN** I see executable percent as the primary metric
- **AND** I see supporting counts for tails, spares, loadouts, crew, and airborne
- **AND** I see a next-action derived from the most common blocker

### Requirement: Process funnel

#### Scenario: Process funnel tracks generation steps

- **GIVEN** sorties at mixed stages
- **WHEN** I view the generation process
- **THEN** counts are shown for planned, tail, loadout, crewed, crew-ready, and airborne

### Requirement: Exceptions

#### Scenario: Exceptions list the gaps

- **GIVEN** one or more sorties are missing tail, spare, loadout, crew, ER, or have config mismatch
- **WHEN** I view exceptions
- **THEN** each incomplete line lists its blockers
- **AND** crew-ready or airborne lines are not listed as exceptions
