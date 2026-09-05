from datetime import datetime

import requests

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from baby_drugs.services.sms import Send_SMS_API


# =========================================================
# TEST MODE
#
# True  = Send SMS immediately
# False = Only send when drug is within 10 minutes
# =========================================================

TEST_MODE = True


# =========================================================
# CHECK DRUG SMS
# =========================================================

def check_drug_sms(baby_id, phone_number):


    print("========================================")
    print("CHECKING UPCOMING DRUG")
    print("========================================")


    # =====================================================
    # GET UPCOMING DRUGS
    # =====================================================

    try:

        response = requests.get(

            settings.UPCOMING_API_URL,

            params={
                "baby_id": baby_id,
            },

            timeout=30,

        )


        response.raise_for_status()


        data = response.json()


    except Exception as error:

        print(
            f"❌ Could not get upcoming drugs: {error}"
        )

        return False


    # =====================================================
    # GET FIRST UPCOMING DRUG
    # =====================================================

    next_drug = data.get(
        "next_drug"
    )


    if not next_drug:

        print("No upcoming drugs.")

        return False


    # =====================================================
    # GET DRUG INFORMATION
    # =====================================================

    drug_name = next_drug.get(
        "drug_name",
        "Medicine"
    )


    amount = next_drug.get(
        "amount",
        ""
    )


    unit = next_drug.get(
        "unit",
        ""
    )


    scheduled_date = next_drug.get(
        "scheduled_date"
    )


    scheduled_time = next_drug.get(
        "scheduled_time"
    )


    # =====================================================
    # VALIDATE DATE AND TIME
    # =====================================================

    if not scheduled_date or not scheduled_time:

        print(
            "❌ Upcoming drug has no date or time."
        )

        return False


    # =====================================================
    # PARSE SCHEDULED DATETIME
    # =====================================================

    try:

        scheduled_datetime = datetime.strptime(

            f"{scheduled_date} {scheduled_time}",

            "%Y-%m-%d %H:%M:%S"

        )


        scheduled_datetime = timezone.make_aware(

            scheduled_datetime,

            timezone.get_current_timezone()

        )


    except ValueError as error:

        print(
            f"❌ Invalid schedule datetime: {error}"
        )

        return False


    # =====================================================
    # CURRENT TIME
    # =====================================================

    now = timezone.now()


    # =====================================================
    # CALCULATE MINUTES UNTIL MEDICINE
    # =====================================================

    seconds_until = (

        scheduled_datetime - now

    ).total_seconds()


    minutes_until = (

        seconds_until / 60

    )


    # =====================================================
    # DISPLAY INFORMATION
    # =====================================================

    print()
    print(f"💊 Next drug: {drug_name}")
    print(f"📅 Scheduled: {scheduled_datetime}")
    print(f"⏱ Minutes away: {minutes_until:.2f}")
    print()


    # =====================================================
    # TEST MODE
    # =====================================================

    if TEST_MODE:

        print(
            "🧪 TEST MODE ENABLED"
        )

        print(
            "SMS will be sent immediately."
        )


    # =====================================================
    # REAL MODE
    #
    # Only send when medicine is 0–10 minutes away
    # =====================================================

    else:

        if not (
            0 <= minutes_until <= 10
        ):

            print(
                "⏳ Drug is not within 10 minutes yet."
            )

            return False


        print(
            "🔔 Drug is within 10 minutes!"
        )


    # =====================================================
    # UNIQUE OCCURRENCE ID
    # =====================================================

    occurrence_id = next_drug.get(
        "occurrence_id"
    )


    if not occurrence_id:

        occurrence_id = (

            f"drug-"
            f"{next_drug.get('id')}-"
            f"{scheduled_date}"

        )


    # =====================================================
    # CACHE KEY
    #
    # Prevent duplicate SMS messages
    # =====================================================

    cache_key = (

        f"drug_sms_sent:"
        f"{baby_id}:"
        f"{occurrence_id}"

    )


    # =====================================================
    # CHECK IF ALREADY SENT
    # =====================================================

    already_sent = cache.get(
        cache_key
    )


    if already_sent:

        print(
            "⚠️ SMS already sent for this medicine."
        )

        return False


    # =====================================================
    # BUILD DOSE
    # =====================================================

    dose = " ".join(

        str(value)

        for value in [amount, unit]

        if value not in [None, ""]

    )


    # =====================================================
    # BUILD SMS MESSAGE
    # =====================================================

    message = (

        f"REMINDER: {drug_name}"

    )


    if dose:

        message += f" ({dose})"


    message += (

        f" is scheduled at "
        f"{scheduled_datetime.strftime('%H:%M')}. "
        f"Please prepare the medicine."

    )


    # =====================================================
    # DISPLAY MESSAGE
    # =====================================================

    print()
    print("========================================")
    print("📱 SENDING SMS")
    print("========================================")

    print(message)

    print("========================================")
    print()


    # =====================================================
    # SEND SMS
    # =====================================================

    try:

        sms = Send_SMS_API(

            phone_number,

            message,

        )


        success = sms.send_sms()


    except Exception as error:

        print(
            f"❌ SMS error: {error}"
        )

        return False


    # =====================================================
    # MARK AS SENT
    #
    # Cache for 24 hours
    # =====================================================

    if success:

        cache.set(

            cache_key,

            True,

            timeout=60 * 60 * 24,

        )


        print()

        print(
            f"✅ SMS sent successfully to "
            f"{phone_number}"
        )


        return True


    else:

        print(
            "❌ SMS failed."
        )

        return False