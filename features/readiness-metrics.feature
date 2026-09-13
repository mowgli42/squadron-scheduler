Feature: Readiness Metrics
  As a squadron scheduler
  I want executable percent and aircraft-risk signals
  So that I know if today's go can generate and what to fix

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
