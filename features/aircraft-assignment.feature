Feature: Aircraft Assignment
  As a squadron scheduler
  I want primary and spare tails with turn and config rules
  So that jets are not double-booked or misconfigured

  Scenario: Assign aircraft to sortie
    Given a sortie without a primary aircraft
    And an available mission-capable aircraft
    When I assign that aircraft as primary
    Then the sortie shows the tail number
    And its process stage becomes at least tail assigned

  Scenario: Reject NMC aircraft
    Given an aircraft with status NMC
    When I attempt to assign it as primary
    Then the system rejects the assignment with a clear conflict message

  Scenario: Reject overlapping aircraft window
    Given an aircraft is primary on a sortie whose window overlaps another
    When I attempt to assign that aircraft to the overlapping sortie
    Then the system rejects the assignment with a clear conflict message

  Scenario: Allow non-overlapping same-day reuse
    Given an aircraft has landed and the turn buffer has elapsed
    When I assign that aircraft to a later sortie
    Then the assignment is accepted

  Scenario: Assign spare aircraft
    Given a sortie with a primary tail
    And another MC aircraft free in that window
    When I assign the second aircraft as spare
    Then the sortie records spare_tail

  Scenario: Spare cannot equal primary
    Given a sortie with primary 87-0321
    When I attempt to set spare to 87-0321
    Then the system rejects the assignment

  Scenario: Config mismatch blocker
    Given a sortie with primary aircraft configured A/A
    When an A/G loadout template is applied
    Then the sortie lists a config mismatch blocker
