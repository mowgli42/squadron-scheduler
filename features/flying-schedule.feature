Feature: Flying Schedule
  As a squadron scheduler
  I want a process-aware board with line identity
  So that I can work today's go in desk language

  Scenario: View schedule board
    Given sorties exist for the current day
    When I open the schedule board
    Then I see sorties ordered by takeoff time
    And each sortie shows stage, mission, line, callsign, tail, spare, loadout, pilot, WSO, ER, and status

  Scenario: Line identity on board
    Given the four-ship morning go is seeded
    When I list sorties
    Then each line has a distinct line_number and non-empty callsign
