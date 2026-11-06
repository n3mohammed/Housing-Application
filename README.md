# Housing Application Prototype

A small Python service and terminal interface demonstrating a housing
application and resident appointment workflow with executable
Behaviour-Driven Development scenarios.

## Run the prototype

```sh
python3 housing_service.py
```

The terminal app saves applications and appointments in the local
`housing_data.json` file, so status checks and appointment lookups still work
after restarting it. The data file is excluded from Git because it may contain
applicant information. The menu
lets you register applications, check application status, book an appointment,
and view appointment details. To book, use an application ID created during
the current run, the matching applicant name, a date in `DD/MM/YYYY` format,
and a time such as `10:00 AM`. Each application can have one appointment.

## Run the Behave scenarios

Install the one test dependency and run Behave from the project root:

```sh
python3 -m pip install -r requirements.txt
python3 -m behave
```

The scenarios in `features/housing.feature` invoke the actual
`HousingApplicationService` through the step definitions in `features/steps/`.
The feature file also covers booking an appointment and checking its details.

## Example eligibility assumptions

For demonstration only, the prototype accepts a complete application when
annual household income is at most £30,000 and household size is at least one.
The system rejects incomplete submissions and explains which required fields
are missing. These are illustrative assumptions, not claims about UK housing
legislation or any real public authority's policy.
