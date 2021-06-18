#!/usr/bin/env python3

import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json, os
from datetime import datetime


url = 'https://cityservices.baltimorecity.gov/water/'
data_file = os.path.abspath(os.path.dirname(__file__)) + '/waterbill.json'


def checkBill(address):

    # Opens the city waterbill page
    print("Connecting...")
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')

    # Creates a dictionary for the hidden form data needed for the request
    data = {}
    inputs = soup.find_all('input', type="hidden", value=True)
    for x in inputs:
        data[x['name']] = x['value']
    data['ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder'
         '$ucServiceAddress$txtServiceAddress'] = address
    data['ctl00$ctl00$rootMasterContent$LocalContentPlaceHolder'
         '$btnGetInfoServiceAddress'] = 'Get Info'
    post_data = urllib.parse.urlencode(data).encode('ascii')

    # Sends form data and receives the water bill form
    post = urllib.request.urlopen(url, data=post_data)
    postsoup = BeautifulSoup(post, 'html.parser')
    bal = postsoup.find(
        id='ctl00_ctl00_rootMasterContent_'
        'LocalContentPlaceHolder_lblCurrentBalance').text
    print(f'Current balance is {bal}')
    return bal


def pushbulletmsg(message, key):
    try:
        pb = Pushbullet(key)
    except:
        print("Something went wrong connecting to pushbullet")
    else:
        push = pb.push_note("Waterbill", message)
        print(push)
    return


def sendEmail(message, address):
    os.system(f'echo "{message}" | mail -s "Waterbill" {address}')
    return


def sendMessage(message, home):
    if 'pushbullet_key' in home:
        try:
            from pushbullet import Pushbullet
            pushbulletmsg(message, home['pushbullet_key'])
        except ImportError:
            print('Please install the pushbullet.py module to notify through pushbullet')
    if 'email' in home: sendEmail(message, home['email'])
    if ('pushbullet_key' not in home and 'email' not in home):
        print('Add email or pushbullet key to waterbill.json to send messages')


if __name__ == "__main__":

    # Open and read a json file with address and previous bill amounts
    with open(data_file, "r") as json_file:
        homes = json.load(json_file)

    # Cycle through addresses, check bill, and update json
    for home in homes:
        try:
            balance = float(checkBill(home["address"])[1:])
        except:
            print("Error fetching current water bill")
        else:
            if balance != home['current_amount']:
                if balance == 0.0:
                    home['history'] = [
                        {
                            "date": datetime.now().strftime("%x"),
                            "change": "paid",
                            "amount": home['current_amount']
                        }
                    ]
                    sendMessage("Your water bill has been paid", home)
                else:
                    newBill = {
                        "date": datetime.now().strftime("%x"),
                        "change": "billed",
                        "amount": balance - home['current_amount']
                    }
                    home['history'].append(newBill)
                    sendMessage(f"Your new water bill is \{balance}", home)
                
                home['date_changed'] = datetime.now().strftime("%x")
                home['current_amount'] = balance

            else:
                days = (datetime.now()-datetime.strptime(home['date_changed'], "%x")).days
                if days >= home['reminder_days'] and home['reminder_days'] != 0 and home['current_amount'] != 0.0:
                    sendMessage(f"Don't forget to pay your water bill of {balance}!", home)

    # Writes new values to the json json_file
    with open(data_file, "w") as json_file:
        json.dump(homes, json_file,indent=2)
