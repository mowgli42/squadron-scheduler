Feature: Squadron Flying Schedule
  As a squadron scheduler
  I want to assign aircraft, loadouts, and crew to sorties
  So that the daily flying schedule is coordinated and executable

  Background:
    Given a squadron with seeded aircraft, aircrew, and sorties
    And the system uses a light-grey IxDF-inspired schedule board

  Scenario: View schedule board
    Given sorties exist for the current day
    When I open the schedule board
    Then I see sorties ordered by takeoff time
    And each sortie shows mission, tail, loadout, pilot, WSO, and status

  Scenario: Assign aircraft to sortie
    Given a sortie without a primary aircraft
    And an available mission-capable aircraft
    When I assign that aircraft as primary
    Then the sortie shows the tail number

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

  Scenario: Reject same-day crew conflict
    Given an aircrew member already assigned to another sortie the same day
    When I attempt to assign them again
    Then the system rejects the assignment with a clear conflict message

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
  Scenario: Mark aircraft crew-ready
    Given a sortie with aircraft, loadout, and full crew
    And maintenance has completed loading and signed the Exceptional Release
    When the aircraft status is set to crew-ready
    Then the sortie is executable

  @wip
  Scenario: Daily change (pen-and-ink)
    Given a published schedule
    When I change a tail or swap crew
    Then the change is logged
    And the board reflects the update immediately
