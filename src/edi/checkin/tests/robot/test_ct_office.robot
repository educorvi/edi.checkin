# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.checkin -t test_office.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.checkin.testing.EDI_CHECKIN_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/checkin/tests/robot/test_office.robot
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

Scenario: As a site administrator I can add a Office
  Given a logged-in site administrator
    and an add Office form
   When I type 'My Office' into the title field
    and I submit the form
   Then a Office with the title 'My Office' has been created

Scenario: As a site administrator I can view a Office
  Given a logged-in site administrator
    and a Office 'My Office'
   When I go to the Office view
   Then I can see the Office title 'My Office'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Office form
  Go To  ${PLONE_URL}/++add++Office

a Office 'My Office'
  Create content  type=Office  id=my-office  title=My Office

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Office view
  Go To  ${PLONE_URL}/my-office
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Office with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Office title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
