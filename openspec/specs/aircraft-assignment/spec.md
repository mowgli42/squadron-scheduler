# Aircraft Assignment

## Purpose

Treat aircraft as scarce time-bound assets: primary and spare tails, mission
capability, configuration fit, and turn conflicts across overlapping windows.

## Requirements

### Requirement: Assign primary aircraft

The system SHALL assign a mission-capable (MC or PMC) aircraft as primary tail.

#### Scenario: Assign aircraft to sortie

- **GIVEN** a sortie without a primary aircraft
- **AND** an available mission-capable aircraft
- **WHEN** I assign that aircraft as primary
- **THEN** the sortie shows the tail number
- **AND** its process stage becomes at least tail assigned

#### Scenario: Reject NMC aircraft

- **GIVEN** an aircraft with status NMC
- **WHEN** I attempt to assign it as primary
- **THEN** the system rejects the assignment with a clear conflict message

### Requirement: Turn / overlap conflict

The system SHALL reject assigning a tail whose flight window overlaps another
sortie where it is already primary or spare (including a turn buffer).

#### Scenario: Reject overlapping aircraft window

- **GIVEN** aircraft 87-0321 is primary on a sortie from 08:00–09:30
- **AND** another sortie takes off at 09:00 the same day
- **WHEN** I attempt to assign 87-0321 as primary or spare to the second sortie
- **THEN** the system rejects the assignment with a clear conflict message

#### Scenario: Allow non-overlapping same-day reuse

- **GIVEN** aircraft 87-0321 lands at 09:30 with turn buffer satisfied
- **AND** a later sortie takes off after the buffer
- **WHEN** I assign 87-0321 to the later sortie
- **THEN** the assignment is accepted

### Requirement: Spare tail

Each sortie SHALL support an optional spare / backup tail distinct from primary.

#### Scenario: Assign spare aircraft

- **GIVEN** a sortie with a primary tail
- **AND** another MC aircraft free in that window
- **WHEN** I assign the second aircraft as spare
- **THEN** the sortie records `spare_tail`
- **AND** spare coverage counts toward readiness metrics

#### Scenario: Spare cannot equal primary

- **GIVEN** a sortie with primary 87-0321
- **WHEN** I attempt to set spare to 87-0321
- **THEN** the system rejects the assignment

### Requirement: Configuration fit

When a loadout template is applied, the system SHALL flag a blocker if the
assigned aircraft configuration is incompatible with that template.

#### Scenario: Config mismatch blocker

- **GIVEN** a sortie with primary aircraft configured `A/A`
- **WHEN** an `A/G` loadout template is applied
- **THEN** the sortie lists a `config mismatch` blocker
- **AND** the line is not treated as clear of exceptions
