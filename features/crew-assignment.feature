Feature: Crew Assignment
  As a squadron scheduler
  I want role-matched crew with rest and replace
  So that positions stay legal and pen-and-ink swaps work

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
