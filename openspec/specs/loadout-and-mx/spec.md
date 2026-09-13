# Loadout and MX

## Purpose

Apply weapons/fuel templates, surface load-crew effort, and gate executable
status on Exceptional Release (ER).

## Requirements

### Requirement: Loadout templates

The system SHALL apply named templates (A/A, A/G, SEAD, clean) to a sortie.

#### Scenario: Apply loadout template

- **GIVEN** a sortie
- **WHEN** I apply an "A/A", "A/G", "SEAD", or "clean" loadout template
- **THEN** the sortie records the template weapons and fuel text
- **AND** a load-crew estimate in minutes is visible on the sortie

### Requirement: Exceptional Release

Crew-ready SHALL require an ER signature attribute on the sortie.

#### Scenario: Block crew-ready without ER

- **GIVEN** a sortie with aircraft, loadout, and full crew
- **AND** ER is not signed
- **WHEN** I set status to "crew-ready"
- **THEN** the system rejects the change with a clear message

#### Scenario: ER enables crew-ready

- **GIVEN** a sortie with aircraft, loadout, and full crew
- **AND** maintenance has signed the Exceptional Release
- **WHEN** I set status to "crew-ready"
- **THEN** the board shows crew-ready and the line is executable
