Feature: Loadout and MX
  As a squadron scheduler
  I want loadout templates, load-crew estimates, and ER gating
  So that weapons and release state are visible before step

  Scenario: Apply loadout template
    Given a sortie
    When I apply an "A/A", "A/G", "SEAD", or "clean" loadout template
    Then the sortie records the template weapons and fuel text
    And a load-crew estimate in minutes is visible on the sortie

  Scenario: Block crew-ready without ER
    Given a sortie with aircraft, loadout, and full crew
    And ER is not signed
    When I set status to "crew-ready"
    Then the system rejects the change with a clear message

  Scenario: ER enables crew-ready
    Given a sortie with aircraft, loadout, and full crew
    And maintenance has signed the Exceptional Release
    When I set status to "crew-ready"
    Then the board shows crew-ready and the line is executable
