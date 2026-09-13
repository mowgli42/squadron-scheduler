Feature: Demo Buildup
  As a squadron scheduler
  I want to replay empty board through launch
  So that process and metrics are teachable

  Scenario: Demo build-up stages
    Given the sample four-ship morning go
    When I apply demo stages 01 through 06 in order
    Then executable percent moves from 0 to 100
    And the board progresses from empty assignments to lead elements airborne
    And stages that claim crew-ready also mark ER signed and spares assigned
