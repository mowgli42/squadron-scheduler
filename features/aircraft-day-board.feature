Feature: Aircraft Day Board
  As a squadron scheduler
  I want an asset view of each jet's day
  So that I can see commitments as primary or spare

  Scenario: View aircraft day board
    Given tails are assigned on one or more sorties
    When I request the aircraft schedule for the day
    Then each aircraft lists status, config, and timed commitments
    And unassigned MC or PMC jets appear with an empty commitment list
