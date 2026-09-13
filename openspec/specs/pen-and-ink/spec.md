# Pen and Ink

## Purpose

Every material schedule change (tail, spare, crew, status, ER) is a dated event
the desk can review.

## Requirements

### Requirement: Change log

#### Scenario: Daily change (pen-and-ink)

- **GIVEN** a published schedule line
- **WHEN** I change a tail, spare, or swap crew
- **THEN** the change is logged with timestamp, field, old value, and new value
- **AND** the board and metrics refresh immediately

#### Scenario: List recent changes

- **GIVEN** one or more pen-and-ink events exist
- **WHEN** I request the change log
- **THEN** events are returned newest-first
