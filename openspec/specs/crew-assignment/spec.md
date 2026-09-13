# Crew Assignment

## Purpose

Fill pilot and WSO positions with role-matched aircrew, enforce same-window and
rest conflicts, and allow pen-and-ink replacement.

## Requirements

### Requirement: Assign crew positions

#### Scenario: Assign crew positions

- **GIVEN** a sortie needing one pilot and one WSO
- **AND** aircrew with matching roles
- **WHEN** I assign a pilot and a WSO
- **THEN** the positions are filled on the board
- **AND** the process stage becomes crewed when both are filled

### Requirement: Same-window crew conflict

#### Scenario: Reject overlapping crew assignment

- **GIVEN** an aircrew member already assigned to another sortie whose window
  overlaps
- **WHEN** I attempt to assign them again
- **THEN** the system rejects the assignment with a clear conflict message

### Requirement: Rest gate

#### Scenario: Block on insufficient rest

- **GIVEN** aircrew with `rest_until` after the sortie takeoff
- **WHEN** I attempt to assign them
- **THEN** the system rejects the assignment with a clear conflict message

### Requirement: Replace crew

#### Scenario: Replace filled position

- **GIVEN** a sortie with a pilot already assigned
- **WHEN** I assign a different eligible pilot to that position
- **THEN** the new pilot replaces the previous assignment
- **AND** a pen-and-ink change is logged
