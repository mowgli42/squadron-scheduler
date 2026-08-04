Feature: Squadron Flying Schedule
  As a squadron scheduler
  I want to assign aircraft, loadouts, and crew to sorties
  So that the weekly flying schedule is coordinated, legal, and executable

  Background:
    Given a squadron with aircraft, aircrew, and mission templates
    And the system uses light-grey IxDF-inspired UI

  Scenario: View weekly schedule board
    Given sorties exist for the current week
    When I open the schedule board
    Then I see sorties ordered by takeoff time
    And each sortie shows tail, loadout, and assigned crew

  Scenario: Assign aircraft to sortie
    Given a sortie without a primary aircraft
    And an available mission-capable aircraft matching the required configuration
    When I assign that aircraft as primary
    Then the sortie shows the tail number
    And the aircraft is marked reserved for that time window

  Scenario: Apply loadout template
    Given a sortie with mission type "A/A"
    When I apply the "A/A standard" loadout template
    Then the sortie records the required weapons stations and fuel
    And load-crew estimate is visible

  Scenario: Assign qualified crew
    Given a sortie needing one pilot and one WSO
    And aircrew with current qualifications and sufficient rest
    When I assign a qualified pilot and WSO
    Then the positions are filled
    And any currency or rest conflict is blocked

  Scenario: Detect conflict
    Given an aircrew member already assigned to another overlapping sortie
    When I attempt to assign them again
    Then the system rejects the assignment with a clear conflict message

  Scenario: Mark aircraft crew-ready
    Given a sortie with aircraft, loadout, and full crew
    And maintenance has completed loading and signed the Exceptional Release
    When the aircraft status is set to crew-ready
    Then the sortie is executable

  Scenario: Daily change (pen-and-ink)
    Given a published weekly schedule
    When I change a tail or swap crew for a single day
    Then the change is logged
    And the daily view reflects the update immediately
