Feature: Squadron Flying Schedule
  As a squadron scheduler
  I want process-aware assignment of aircraft, loadouts, and crew
  So that I can see whether today's go is executable and what to fix next

  Background:
    Given a squadron with seeded aircraft, aircrew, and sorties
    And the board uses an IxDF decision-first layout

  Scenario: View schedule board
    Given sorties exist for the current day
    When I open the schedule board
    Then I see sorties ordered by takeoff time
    And each sortie shows stage, mission, tail, loadout, pilot, WSO, and status

  Scenario: Readiness metrics answer the primary question
    Given the four-ship morning go is on the board
    When I view the dashboard
    Then I see executable percent as the primary metric
    And I see supporting counts for tails, loadouts, crew, and airborne
    And I see a next-action derived from the most common blocker

  Scenario: Process funnel tracks generation steps
    Given sorties at mixed stages
    When I view the generation process
    Then counts are shown for planned, tail, loadout, crewed, crew-ready, and airborne

  Scenario: Exceptions list the gaps
    Given one or more sorties are missing tail, loadout, or crew
    When I view exceptions
    Then each incomplete line lists its blockers
    And crew-ready or airborne lines are not listed as exceptions

  Scenario: Assign aircraft to sortie
    Given a sortie without a primary aircraft
    And an available mission-capable aircraft
    When I assign that aircraft as primary
    Then the sortie shows the tail number
    And its process stage becomes tail assigned

  Scenario: Reject same-day aircraft conflict
    Given an aircraft already assigned to another sortie the same day
    When I attempt to assign that aircraft again
    Then the system rejects the assignment with a clear conflict message

  Scenario: Apply loadout template
    Given a sortie
    When I apply an "A/A", "A/G", "SEAD", or "clean" loadout template
    Then the sortie records the template weapons and fuel text

  Scenario: Assign crew positions
    Given a sortie needing one pilot and one WSO
    And aircrew with matching roles
    When I assign a pilot and a WSO
    Then the positions are filled on the board
    And the process stage becomes crewed

  Scenario: Reject same-day crew conflict
    Given an aircrew member already assigned to another sortie the same day
    When I attempt to assign them again
    Then the system rejects the assignment with a clear conflict message

  Scenario: Advance status to crew-ready and airborne
    Given a sortie with aircraft, loadout, and full crew
    When I set status to "crew-ready"
    Then the board shows crew-ready and the line is executable
    When I set status to "airborne"
    Then the board shows airborne

  Scenario: Demo build-up stages
    Given the sample four-ship morning go
    When I apply demo stages 01 through 06 in order
    Then executable percent moves from 0 to 100
    And the board progresses from empty assignments to lead elements airborne

  @wip
  Scenario: Block on rest or currency
    Given aircrew with insufficient rest or expired currency
    When I attempt to assign them
    Then the system rejects the assignment with a clear conflict message

  @wip
  Scenario: Show load-crew estimate
    Given a sortie with a loadout template applied
    When I view the sortie
    Then a load-crew estimate is visible

  @wip
  Scenario: Exceptional Release as a signed event
    Given a sortie with aircraft, loadout, and full crew
    And maintenance has signed the Exceptional Release
    When the aircraft is marked crew-ready
    Then the change is attributed to MX and the sortie is executable

  @wip
  Scenario: Daily change (pen-and-ink)
    Given a published schedule
    When I change a tail or swap crew
    Then the change is logged
    And the board and metrics refresh immediately
