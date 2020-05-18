#!/usr/bin/env python3

import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pushbullet import Pushbullet

url = 'https://cityservices.baltimorecity.gov/water/'
file = './waterbill.json'

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


if __name__ == "__main__":

    # Open and read a json file with address and previous bill amounts
    with open(file, "r") as json_file:
        homes = json.load(json_file)

    # Cycle through addresses, check bill, and update json
    for home in homes:
        try:
            balance = checkBill(home["address"])
        except:
            print("Error fetching current water bill")
        else:
            if balance != home['current_amount']:
                home['date_changed'] = datetime.now().strftime("%x")
                home['current_amount'] = balance
                if balance == "$.00":
                    pushbulletmsg("Your water bill has been paid", home['pushbullet_key'])
                else:
                    pushbulletmsg(f"Your new water bill is {balance}", home['pushbullet_key'])
            else:
                days = (datetime.now()-datetime.strptime(home['date_changed'], "%x")).days
                if days >= 5 and home['current_amount'] != "$.00":
                    pushbulletmsg(f"Don't forget to pay your water bill of {balance}!", home['pushbullet_key'])

    # Writes new values to the json json_file
    with open(file, "w") as json_file:
        json.dump(homes, json_file,indent=2)