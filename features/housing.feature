Feature: Housing application eligibility and management
  As a housing applicant
  I want to submit an application and check its status
  So that I can understand the outcome of my application

  Scenario: Submit a complete application that meets the example criteria
    Given a new housing application service
    When I submit an application for "Alex Green" with annual income 24000 and household size 2
    Then the application should be accepted
    And the application should have an application ID

  Scenario: Reject an incomplete application and explain missing information
    Given a new housing application service
    When I submit an application with no name, no income and household size 2
    Then the application should be rejected
    And the rejection reasons should include "Applicant name is required."
    And the rejection reasons should include "Annual income is required."

  Scenario: Check eligibility for an applicant within the example threshold
    Given a new housing application service
    When I submit an application for "Sam Lee" with annual income 30000 and household size 1
    Then the application should be accepted

  Scenario: Reject an application above the example income threshold
    Given a new housing application service
    When I submit an application for "Taylor Jones" with annual income 42000 and household size 3
    Then the application should be rejected
    And the rejection reasons should include "Annual household income must be no more than £30,000."

  Scenario: Check the status of an existing application
    Given a new housing application service
    When I submit an application for "Morgan Reed" with annual income 18000 and household size 1
    And I look up the submitted application
    Then the looked-up application status should be "Accepted"

  Scenario: Book and retrieve a resident appointment for an application
    Given a new housing application service
    When I submit an application for "John Smith" with annual income 20000 and household size 2
    And I book an appointment for the submitted application on "10/11/2026" at "10:00 AM"
    Then the appointment should be confirmed for "John Smith"
    And the appointment date and time should be "10/11/2026" and "10:00 AM"
