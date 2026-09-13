Feature: Pen and Ink
  As a squadron scheduler
  I want every material change logged
  So that the published schedule has an audit trail

  Scenario: Daily change (pen-and-ink)
    Given a published schedule line
    When I change a tail, spare, or swap crew
    Then the change is logged with timestamp, field, old value, and new value
    And the board and metrics refresh immediately

  Scenario: List recent changes
    Given one or more pen-and-ink events exist
    When I request the change log
    Then events are returned newest-first
