# Baltimore Water Bill Checker

The current system for water bill payment in Baltimore City requires either waiting for a paper bill or periodically checking the city website for your address. To automate this a little, I put together this script that can be run to check for a bill and message my phone if it has updated.

## Requirements
* Python 3
* Pushbullet.py python library with API key set up on phone/computer, or outgoing mail server installed
* Beautiful Soup 4 python library

## Usage

Set up a crontab or other scheduler to run checkwaterbill.py as often as you're comfortable. The script saves its data into a json file in the same directory (so make sure script is run from that directory). This json file waterbill.json must take the format:
```javascript
[
    {
        "address": "123 Example St",
        "current_amount": 0.00,
        "date_changed": "03/27/20",
        "pushbullet_key": "YourPushBulletAPIKey",
        "email": "youremail@example.com",
        "output_file": "/home/user/WaterBill/bill.json",
        "history": []
    }
]
```
The pushbullet key, email, and output_file are optional. Without them, the script will simply save bill history to the json file.
The output_file is just a second location to save the results (making it easier for other scripts to use)

Most phone carriers have a email to text option, such as verizon, allowing you to send mail to yournumber@vtext.com