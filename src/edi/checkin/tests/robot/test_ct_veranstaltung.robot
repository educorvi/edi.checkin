# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.checkin -t test_veranstaltung.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.checkin.testing.EDI_CHECKIN_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/checkin/tests/robot/test_veranstaltung.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Veranstaltung
  Given a logged-in site administrator
    and an add Office form
   When I type 'My Veranstaltung' into the title field
    and I submit the form
   Then a Veranstaltung with the title 'My Veranstaltung' has been created

Scenario: As a site administrator I can view a Veranstaltung
  Given a logged-in site administrator
    and a Veranstaltung 'My Veranstaltung'
   When I go to the Veranstaltung view
   Then I can see the Veranstaltung title 'My Veranstaltung'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Office form
  Go To  ${PLONE_URL}/++add++Office

a Veranstaltung 'My Veranstaltung'
  Create content  type=Office  id=my-veranstaltung  title=My Veranstaltung

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Veranstaltung view
  Go To  ${PLONE_URL}/my-veranstaltung
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Veranstaltung with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Veranstaltung title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
