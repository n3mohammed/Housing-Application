"""Small, in-memory housing application prototype.

Eligibility thresholds below are illustrative assumptions for this prototype;
they do not represent UK housing law or any real council's policy.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional


# Example-only rules, deliberately easy to change for a demonstration.
MAX_ANNUAL_HOUSEHOLD_INCOME = 30_000
MIN_HOUSEHOLD_SIZE = 1


@dataclass
class HousingApplication:
    application_id: str
    applicant_name: str
    annual_income: Optional[float]
    household_size: Optional[int]
    status: str
    reasons: List[str] = field(default_factory=list)


@dataclass
class ResidentAppointment:
    application_id: str
    applicant_name: str
    appointment_date: str
    appointment_time: str
    status: str = "Confirmed"


class HousingApplicationService:
    """Registers applications, optionally saving them to a local JSON file."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.applications: Dict[str, HousingApplication] = {}
        self.appointments: Dict[str, ResidentAppointment] = {}
        self._next_id = 1
        self.storage_path = Path(storage_path) if storage_path else None
        if self.storage_path:
            self._load()

    def _load(self) -> None:
        """Load saved applications and appointments when a data file exists."""
        if not self.storage_path or not self.storage_path.exists():
            return
        try:
            saved_data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.applications = {
                item["application_id"]: HousingApplication(**item)
                for item in saved_data.get("applications", [])
            }
            self.appointments = {
                item["application_id"]: ResidentAppointment(**item)
                for item in saved_data.get("appointments", [])
            }
            used_numbers = [
                int(application_id.split("-")[-1])
                for application_id in self.applications
                if application_id.startswith("HA-")
                and application_id.split("-")[-1].isdigit()
            ]
            self._next_id = max(used_numbers, default=0) + 1
        except (OSError, json.JSONDecodeError, TypeError, KeyError) as error:
            raise RuntimeError(
                f"Could not read saved housing data at {self.storage_path}: {error}"
            ) from error

    def _save(self) -> None:
        """Write current records to the configured local data file."""
        if not self.storage_path:
            return
        saved_data = {
            "applications": [
                {
                    "application_id": item.application_id,
                    "applicant_name": item.applicant_name,
                    "annual_income": item.annual_income,
                    "household_size": item.household_size,
                    "status": item.status,
                    "reasons": item.reasons,
                }
                for item in self.applications.values()
            ],
            "appointments": [
                {
                    "application_id": item.application_id,
                    "applicant_name": item.applicant_name,
                    "appointment_date": item.appointment_date,
                    "appointment_time": item.appointment_time,
                    "status": item.status,
                }
                for item in self.appointments.values()
            ],
        }
        assert self.storage_path is not None
        self.storage_path.write_text(json.dumps(saved_data, indent=2), encoding="utf-8")

    def register_application(
        self,
        applicant_name: Optional[str],
        annual_income: Optional[float],
        household_size: Optional[int],
    ) -> HousingApplication:
        """Create and assess an application, retaining incomplete submissions."""
        application_id = f"HA-{self._next_id:04d}"
        self._next_id += 1
        name = applicant_name.strip() if applicant_name else ""
        reasons: List[str] = []

        if not name:
            reasons.append("Applicant name is required.")
        if annual_income is None:
            reasons.append("Annual income is required.")
        elif annual_income < 0:
            reasons.append("Annual income cannot be negative.")
        if household_size is None:
            reasons.append("Household size is required.")
        elif household_size < 1:
            reasons.append("Household size must be at least 1.")

        if reasons:
            status = "Rejected"
        else:
            reasons = check_eligibility(float(annual_income), int(household_size))
            status = "Accepted" if not reasons else "Rejected"

        application = HousingApplication(
            application_id, name, annual_income, household_size, status, reasons
        )
        self.applications[application_id] = application
        self._save()
        return application

    def get_application(self, application_id: str) -> Optional[HousingApplication]:
        """Return an application by ID, or None if it does not exist."""
        return self.applications.get(application_id)

    def book_appointment(
        self,
        applicant_name: str,
        application_id: str,
        appointment_date: str,
        appointment_time: str,
    ) -> ResidentAppointment:
        """Book an appointment for a known application after validating inputs."""
        application = self.get_application(application_id)
        if application is None:
            raise ValueError("Application ID was not found.")
        if applicant_name.strip().casefold() != application.applicant_name.casefold():
            raise ValueError("Applicant name does not match the application.")
        if application_id in self.appointments:
            raise ValueError("An appointment is already booked for this application.")
        try:
            datetime.strptime(appointment_date, "%d/%m/%Y")
        except ValueError as error:
            raise ValueError("Enter the appointment date as DD/MM/YYYY.") from error
        try:
            datetime.strptime(appointment_time, "%I:%M %p")
        except ValueError as error:
            raise ValueError("Enter the appointment time as HH:MM AM/PM.") from error

        appointment = ResidentAppointment(
            application_id=application_id,
            applicant_name=application.applicant_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time.upper(),
        )
        self.appointments[application_id] = appointment
        self._save()
        return appointment

    def get_appointment(self, application_id: str) -> Optional[ResidentAppointment]:
        """Return the appointment for an application, if it has one."""
        return self.appointments.get(application_id)

# Illustrative eligibility rule: the annual household income must not exceed £30,000.
def check_eligibility(annual_income: float, household_size: int) -> List[str]:
    """Return example-rule failure reasons """
    reasons = []
    if annual_income > MAX_ANNUAL_HOUSEHOLD_INCOME:
        reasons.append(
            f"Annual household income must be no more than £{MAX_ANNUAL_HOUSEHOLD_INCOME:,}."
        )
    if household_size < MIN_HOUSEHOLD_SIZE:
        reasons.append(f"Household size must be at least {MIN_HOUSEHOLD_SIZE}.")
    return reasons


def main() -> None:
    """Minimal terminal interface for trying the service manually."""
    # BDD scenarios use the default in-memory service; the CLI saves local data.
    service = HousingApplicationService(Path(__file__).with_name("housing_data.json"))
    print("========================================")
    print(" HOUSING APPLICATION MANAGEMENT SYSTEM")
    print("========================================")
    while True:
        print("\n1. Register new housing application")
        print("2. Check application status")
        print("3. Book resident appointment")
        print("4. View appointment details")
        print("5. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            name = input("Applicant name: ").strip()
            income_text = input("Annual household income (£): ").strip()
            household_text = input("Household size: ").strip()
            try:
                income = float(income_text) if income_text else None
                household_size = int(household_text) if household_text else None
            except ValueError:
                print("Income must be a number and household size must be a whole number.")
                continue
            application = service.register_application(name, income, household_size)
            print(f"Application {application.application_id}: {application.status}")
            for reason in application.reasons:
                print(f"- {reason}")
        elif choice == "2":
            application = service.get_application(input("Application ID: ").strip())
            if application is None:
                print("Application not found.")
            else:
                print(f"{application.application_id}: {application.status}")
                for reason in application.reasons:
                    print(f"- {reason}")
        elif choice == "3":
            print("\n----- RESIDENT APPOINTMENT BOOKING -----\n")
            applicant_name = input("Enter applicant name: ").strip()
            application_id = input("Enter application ID: ").strip()
            appointment_date = input("Enter preferred appointment date (DD/MM/YYYY): ").strip()
            appointment_time = input("Enter preferred appointment time (e.g. 10:00 AM): ").strip()
            try:
                appointment = service.book_appointment(
                    applicant_name, application_id, appointment_date, appointment_time
                )
            except ValueError as error:
                print(f"Appointment could not be booked: {error}")
            else:
                print("\nAppointment booked successfully!")
                print("\nAppointment Details:")
                print(f"Applicant: {appointment.applicant_name}")
                print(f"Application ID: {appointment.application_id}")
                print(f"Date: {appointment.appointment_date}")
                print(f"Time: {appointment.appointment_time}")
                print(f"Status: {appointment.status}")
        elif choice == "4":
            application_id = input("Enter application ID: ").strip()
            appointment = service.get_appointment(application_id)
            if appointment is None:
                print("No appointment found for that application ID.")
            else:
                print("\nAppointment Details:")
                print(f"Applicant: {appointment.applicant_name}")
                print(f"Application ID: {appointment.application_id}")
                print(f"Date: {appointment.appointment_date}")
                print(f"Time: {appointment.appointment_time}")
                print(f"Status: {appointment.status}")
        elif choice == "5":
            break
        else:
            print("Please choose 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()
