from datetime import datetime

import requests

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from baby_drugs.services.sms import Send_SMS_API


# =========================================================
# TEST MODE
#
# True  = Send SMS immediately for testing
# False = Only send when drug is within 10 minutes
# =========================================================

TEST_MODE = True


class Command(BaseCommand):

    help = (
        "Check the first upcoming drug and send "
        "an SMS when it is within 10 minutes."
    )


    # =====================================================
    # COMMAND ARGUMENTS
    # =====================================================

    def add_arguments(self, parser):

        parser.add_argument(

            "--baby-id",

            required=True,

            type=str,

        )


        # Multiple phone numbers allowed
        parser.add_argument(

            "--phones",

            required=True,

            nargs="+",

            type=str,

        )


    # =====================================================
    # MAIN COMMAND
    # =====================================================

    def handle(self, *args, **options):


        baby_id = options["baby_id"]

        phone_numbers = options["phones"]


        # =================================================
        # GET UPCOMING DRUGS
        # =================================================

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


            self.stdout.write(

                self.style.ERROR(

                    f"Could not get upcoming drugs: {error}"

                )

            )

            return


        # =================================================
        # GET FIRST UPCOMING DRUG
        # =================================================

        next_drug = data.get(

            "next_drug"

        )


        if not next_drug:


            self.stdout.write(

                "No upcoming drugs."

            )

            return


        # =================================================
        # GET BABY NAME
        # =================================================

        baby_name = next_drug.get(

            "baby_name",

            "your baby"

        )


        # =================================================
        # GET DRUG INFORMATION
        # =================================================

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


        # =================================================
        # VALIDATE DATE AND TIME
        # =================================================

        if not scheduled_date or not scheduled_time:


            self.stdout.write(

                self.style.ERROR(

                    "Upcoming drug has no date or time."

                )

            )

            return


        # =================================================
        # PARSE SCHEDULED DATETIME
        # =================================================

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


            self.stdout.write(

                self.style.ERROR(

                    f"Invalid schedule datetime: {error}"

                )

            )

            return


        # =================================================
        # CURRENT TIME
        # =================================================

        now = timezone.now()


        # =================================================
        # CALCULATE MINUTES UNTIL MEDICINE
        # =================================================

        seconds_until = (

            scheduled_datetime - now

        ).total_seconds()


        minutes_until = (

            seconds_until / 60

        )


        # =================================================
        # DISPLAY INFORMATION
        # =================================================

        self.stdout.write(

            f"Baby: {baby_name} | "
            f"Next drug: {drug_name} | "
            f"Scheduled: {scheduled_datetime} | "
            f"Minutes away: {minutes_until:.2f}"

        )


        # =================================================
        # TEST MODE
        # =================================================

        if TEST_MODE:


            self.stdout.write(

                self.style.WARNING(

                    "TEST MODE ENABLED: "
                    "SMS will be sent immediately."

                )

            )


        # =================================================
        # REAL MODE
        #
        # Only continue when medicine is 0–10 minutes away
        # =================================================

        else:


            if not (

                0 <= minutes_until <= 10

            ):


                self.stdout.write(

                    "Not within 10 minutes yet."

                )

                return


        # =================================================
        # UNIQUE OCCURRENCE ID
        # =================================================

        occurrence_id = next_drug.get(

            "occurrence_id"

        )


        if not occurrence_id:


            occurrence_id = (

                f"drug-"
                f"{next_drug.get('id')}-"
                f"{scheduled_date}"

            )


        # =================================================
        # CACHE KEY
        #
        # Prevent duplicate SMS messages
        # =================================================

        cache_key = (

            f"drug_sms_sent:"
            f"{baby_id}:"
            f"{occurrence_id}"

        )


        # =================================================
        # CHECK IF ALREADY SENT
        # =================================================

        already_sent = cache.get(

            cache_key

        )


        if already_sent:


            self.stdout.write(

                self.style.WARNING(

                    "SMS already sent for this medicine."

                )

            )

            return


        # =================================================
        # BUILD DOSE
        # =================================================

        dose = " ".join(

            str(value)

            for value in [

                amount,

                unit,

            ]

            if value not in [

                None,

                "",

            ]

        )


        # =================================================
        # BUILD SMS MESSAGE
        # =================================================

        message = (

            f"REMINDER FOR {baby_name.upper()}: "

        )


        message += drug_name


        if dose:


            message += f" ({dose})"


        message += (

            f" is scheduled at "
            f"{scheduled_datetime.strftime('%H:%M')}. "
            f"Please prepare the medicine."

        )


        # =================================================
        # DISPLAY SMS BEFORE SENDING
        # =================================================

        self.stdout.write(

            "Sending message:"

        )


        self.stdout.write(

            message

        )


        # =================================================
        # SEND SMS TO ALL PHONE NUMBERS
        # =================================================

        successful_sends = 0


        for phone_number in phone_numbers:


            try:


                self.stdout.write(

                    f"Sending SMS to {phone_number}..."

                )


                sms = Send_SMS_API(

                    phone_number,

                    message,

                )


                success = sms.send_sms()


                if success:


                    successful_sends += 1


                    self.stdout.write(

                        self.style.SUCCESS(

                            f"SMS sent successfully to "
                            f"{phone_number}"

                        )

                    )


                else:


                    self.stdout.write(

                        self.style.ERROR(

                            f"SMS failed for "
                            f"{phone_number}"

                        )

                    )


            except Exception as error:


                self.stdout.write(

                    self.style.ERROR(

                        f"SMS error for "
                        f"{phone_number}: {error}"

                    )

                )


        # =================================================
        # MARK AS SENT
        #
        # Only mark as sent if at least one SMS succeeded
        # =================================================

        if successful_sends > 0:


            cache.set(

                cache_key,

                True,

                timeout=60 * 60 * 24,

            )


            self.stdout.write(

                self.style.SUCCESS(

                    f"Reminder completed. "
                    f"{successful_sends} SMS message(s) sent."

                )

            )


        else:


            self.stdout.write(

                self.style.ERROR(

                    "No SMS messages were sent successfully."

                )

            )