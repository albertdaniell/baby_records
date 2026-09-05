from datetime import datetime, timedelta
import requests


TEST_MODE = True


def check_upcoming_drug():

    upcoming = get_upcoming_drugs()

    if not upcoming:
        print("No upcoming drugs.")
        return


    # First upcoming drug
    drug = upcoming[0]

    drug_name = drug["drug_name"]
    scheduled_time = drug["scheduled_time"]
    scheduled_date = drug["scheduled_date"]

    print(f"Next drug: {drug_name}")
    print(f"Scheduled: {scheduled_date} {scheduled_time}")


    # ==========================================
    # TEST MODE
    # ==========================================

    if TEST_MODE:

        print("🧪 TEST MODE - Sending SMS immediately")

        message = (
            f"Reminder: {drug_name} is scheduled "
            f"for {scheduled_time}."
        )

        sms = Send_SMS_API(
            "+254728463410",
            message
        )

        sms.send_sms()

        return


    # ==========================================
    # REAL TIME CHECK
    # ==========================================

    scheduled_datetime = datetime.strptime(
        f"{scheduled_date} {scheduled_time}",
        "%Y-%m-%d %H:%M:%S"
    )

    now = datetime.now()

    difference = (
        scheduled_datetime - now
    ).total_seconds() / 60


    print(f"Minutes until drug: {difference}")


    # Send when approximately 10 minutes away

    if 9 <= difference <= 10:

        message = (
            f"💊 Drug Reminder\n\n"
            f"{drug_name} is scheduled in "
            f"approximately 10 minutes.\n\n"
            f"Time: {scheduled_time}"
        )

        sms = Send_SMS_API(
            "+254728463410",
            message
        )

        sms.send_sms()

        print("SMS sent!")

    else:

        print(
            "Drug is not yet 10 minutes away."
        )