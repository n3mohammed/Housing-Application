"""Behave steps exercising the real housing service implementation."""

from behave import given, when, then

from housing_service import HousingApplicationService


@given("a new housing application service")
def step_new_service(context):
    context.service = HousingApplicationService()
    context.application = None
    context.looked_up_application = None


@when('I submit an application for "{name}" with annual income {income} and household size {size}')
def step_submit_application(context, name, income, size):
    context.application = context.service.register_application(
        name, float(income), int(size)
    )


@when("I submit an application with no name, no income and household size {size}")
def step_submit_incomplete_application(context, size):
    context.application = context.service.register_application(None, None, int(size))


@when("I look up the submitted application")
def step_lookup_application(context):
    context.looked_up_application = context.service.get_application(
        context.application.application_id
    )


@when('I book an appointment for the submitted application on "{appointment_date}" at "{appointment_time}"')
def step_book_appointment(context, appointment_date, appointment_time):
    context.appointment = context.service.book_appointment(
        context.application.applicant_name,
        context.application.application_id,
        appointment_date,
        appointment_time,
    )


@then("the application should be accepted")
def step_application_accepted(context):
    assert context.application.status == "Accepted", context.application.reasons


@then("the application should be rejected")
def step_application_rejected(context):
    assert context.application.status == "Rejected"


@then('the rejection reasons should include "{expected_reason}"')
def step_rejection_reason(context, expected_reason):
    assert expected_reason in context.application.reasons


@then("the application should have an application ID")
def step_has_application_id(context):
    assert context.application.application_id
    assert context.service.get_application(context.application.application_id) is context.application


@then('the looked-up application status should be "{expected_status}"')
def step_lookup_status(context, expected_status):
    assert context.looked_up_application is not None
    assert context.looked_up_application.status == expected_status


@then('the appointment should be confirmed for "{applicant_name}"')
def step_appointment_confirmed(context, applicant_name):
    saved_appointment = context.service.get_appointment(
        context.application.application_id
    )
    assert saved_appointment is not None
    assert saved_appointment.applicant_name == applicant_name
    assert saved_appointment.status == "Confirmed"


@then('the appointment date and time should be "{expected_date}" and "{expected_time}"')
def step_appointment_date_time(context, expected_date, expected_time):
    assert context.appointment.appointment_date == expected_date
    assert context.appointment.appointment_time == expected_time
