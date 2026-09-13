# Flying Schedule

## Purpose

Present the day’s sorties as an ordered board with process stage, mission,
aircraft, loadout, crew, and status so the scheduler can work the generation
process.

## Requirements

### Requirement: Sortie board ordered by takeoff

The system SHALL list sorties for the operating day ordered by takeoff time.

#### Scenario: View schedule board

- **GIVEN** sorties exist for the current day
- **WHEN** I open the schedule board
- **THEN** I see sorties ordered by takeoff time
- **AND** each sortie shows stage, mission, line identity, primary tail, spare,
  loadout, pilot, WSO, ER, and status

### Requirement: Line identity

Each sortie SHALL carry a line number and callsign for desk language.

#### Scenario: Line identity on board

- **GIVEN** the four-ship morning go is seeded
- **WHEN** I list sorties
- **THEN** each line has a distinct `line_number` and non-empty `callsign`
