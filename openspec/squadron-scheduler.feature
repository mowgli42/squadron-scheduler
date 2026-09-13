Feature: Squadron Flying Schedule
  As a squadron scheduler
  I want process-aware assignment of aircraft, loadouts, and crew
  So that I can see whether today's go is executable and what to fix next

  Background:
    Given a squadron with seeded aircraft, aircrew, and sorties
    And the board uses an IxDF decision-first layout

  # Capability scenarios live in features/*.feature — this file is the overview.

  Scenario: View schedule board
    Given sorties exist for the current day
    When I open the schedule board
    Then I see sorties ordered by takeoff time
    And each sortie shows stage, mission, line, callsign, tail, spare, loadout, pilot, WSO, ER, and status

  Scenario: Readiness metrics answer the primary question
    Given the four-ship morning go is on the board
    When I view the dashboard
    Then I see executable percent as the primary metric
    And I see supporting counts for tails, spares, loadouts, crew, and airborne
    And I see a next-action derived from the most common blocker

  Scenario: Process funnel tracks generation steps
    Given sorties at mixed stages
    When I view the generation process
    Then counts are shown for planned, tail, loadout, crewed, crew-ready, and airborne

  Scenario: Exceptions list the gaps
    Given one or more sorties are missing tail, spare, loadout, crew, ER, or have config mismatch
    When I view exceptions
    Then each incomplete line lists its blockers
    And crew-ready or airborne lines are not listed as exceptions

  Scenario: Assign aircraft to sortie
    Given a sortie without a primary aircraft
    And an available mission-capable aircraft
    When I assign that aircraft as primary
    Then the sortie shows the tail number
    And its process stage becomes at least tail assigned

  Scenario: Reject overlapping aircraft window
    Given an aircraft is primary on a sortie whose window overlaps another
    When I attempt to assign that aircraft to the overlapping sortie
    Then the system rejects the assignment with a clear conflict message

  Scenario: Assign spare aircraft
    Given a sortie with a primary tail
    And another MC aircraft free in that window
    When I assign the second aircraft as spare
    Then the sortie records spare_tail

  Scenario: Apply loadout template
    Given a sortie
    When I apply an "A/A", "A/G", "SEAD", or "clean" loadout template
    Then the sortie records the template weapons and fuel text
    And a load-crew estimate in minutes is visible on the sortie

  Scenario: Assign crew positions
    Given a sortie needing one pilot and one WSO
    And aircrew with matching roles
    When I assign a pilot and a WSO
    Then the positions are filled on the board
    And the process stage becomes crewed

  Scenario: Reject overlapping crew assignment
    Given an aircrew member already assigned to an overlapping sortie
    When I attempt to assign them again
    Then the system rejects the assignment with a clear conflict message

  Scenario: Block on insufficient rest
    Given aircrew with rest_until after the sortie takeoff
    When I attempt to assign them
    Then the system rejects the assignment with a clear conflict message

  Scenario: Replace filled position
    Given a sortie with a pilot already assigned
    When I assign a different eligible pilot to that position
    Then the new pilot replaces the previous assignment
    And a pen-and-ink change is logged

  Scenario: Block crew-ready without ER
    Given a sortie with aircraft, loadout, and full crew
    And ER is not signed
    When I set status to "crew-ready"
    Then the system rejects the change with a clear message

  Scenario: ER enables crew-ready
    Given a sortie with aircraft, loadout, and full crew
    And maintenance has signed the Exceptional Release
    When I set status to "crew-ready"
    Then the board shows crew-ready and the line is executable

  Scenario: Daily change (pen-and-ink)
    Given a published schedule line
    When I change a tail, spare, or swap crew
    Then the change is logged with timestamp, field, old value, and new value
    And the board and metrics refresh immediately

  Scenario: View aircraft day board
    Given tails are assigned on one or more sorties
    When I request the aircraft schedule for the day
    Then each aircraft lists status, config, and timed commitments

  Scenario: Demo build-up stages
    Given the sample four-ship morning go
    When I apply demo stages 01 through 06 in order
    Then executable percent moves from 0 to 100
    And the board progresses from empty assignments to lead elements airborne
    And stages that claim crew-ready also mark ER signed and spares assigned

  @production
  Scenario: Live Ops-MX feed
    Given aircraft status comes from the maintenance system of record
    When MX marks a jet NMC
    Then the schedule reflects that status without manual edit

  @production
  Scenario: Full RAP currency engine
    Given aircrew with expired mission currency
    When I attempt to assign them
    Then the system rejects the assignment with the governing RAP rule
