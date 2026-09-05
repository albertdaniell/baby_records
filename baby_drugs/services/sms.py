import requests
import json


class Send_SMS_API:

    def __init__(self, number, message):

        self.message = message
        self.number = number


    def send_sms(self):

        url = "https://restapi.smsgateway.co.ke/v1/send"

        payload = [
            {
                "number": self.number,
                "senderID": "KALRO",
                "text": self.message,
                "type": "sms",
                "lifetime": 86400,
                "delivery": False,
            }
        ]


        headers = {
        'X-Access-Token': '0cd441a5c1241bf673c8e177d9363143',
        'Content-Type': 'application/json',
        'Cookie': 'advanced-restapi=ffiooir29c0or7lq1ecitr1agk'
        }


        if not self.number:

            print(f"Failed: {self.number}")

            return False


        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30,
            )


            print(response.text)


            response.raise_for_status()


            return True


        except Exception as error:

            print(f"SMS Error: {error}")

            return False