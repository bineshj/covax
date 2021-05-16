import requests
from email.mime.text import MIMEText
from datetime import date
import smtplib, sys
from datetime import datetime
import time
import subprocess
import pprint,json
import yaml, getopt
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-u", "--userid", dest="user", type="string",
                  help="email address of SMTP user",)
parser.add_option("-p", "--password", dest="password", type="string",
                  help="smtp user password",)

(options, args) = parser.parse_args()

 # get command line parameters
SMTP_USERNAME = options.user
SMTP_PASSWORD = options.password
if not SMTP_USERNAME:
    print ("User not defined. Please run script as below: \nvax_avail.py -u <email_address> -p password")
    sys.exit()
if not SMTP_PASSWORD:
    print ("Password not defined. Please run script as below: \nvax_avail.py -u <email_address> -p password")
    sys.exit()

with open('locations.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

dtime = datetime.now().strftime("%d-%m-%Y")

# Set variables from data.yaml file
PINCODE = data['locations']['search_in']
EXCLUDE_PINCODE = data['locations']['exclude']
frequency = data['frequency'][0]
district_id = data['district_id'][0]
EMAIL_TO = data['EMAIL_TO']

# Gmail serverr default configuration, change according to smtp server provider
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = SMTP_USERNAME

DATE_FORMAT = "%d/%m/%Y"
EMAIL_SPACE = ", "

DATA='This is the content of the email.'
available_list = {}

def send_email(sub, emailTolist, body_msg):
    msg = MIMEText(body_msg)
    msg['Subject'] = sub + " %s" % (date.today().strftime(DATE_FORMAT))
    msg['To'] = EMAIL_SPACE.join(emailTolist)
    msg['From'] = EMAIL_FROM
    mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mail.starttls()
    mail.login(SMTP_USERNAME, SMTP_PASSWORD)
    mail.sendmail(EMAIL_FROM, emailTolist, msg.as_string())
    mail.quit()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

while (True):
    try:
        if district_id:
            weburl = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id=" + str(district_id)+  "&date=" + dtime
            r =requests.get(weburl, headers=headers)
            res = r.json()
            centers = res['centers']
            total_list = {}
            avail_list = {}
            avail_list_array = []
            total_list_array = []
            for cen in centers:
                if str(cen['pincode']) in EXCLUDE_PINCODE:
                    pass
                else:
                    for ses in cen['sessions']:
                        if ses['min_age_limit'] < 19:
                            total_list[cen['address']] = ses['available_capacity']
                            total_list_array.append({"Location":cen['address'], "Available":ses['available_capacity'], "pin":cen['pincode']})
                            if ses['available_capacity'] > 0:
                                sub = "Vaccine update: Avaiable at : " + cen['address']
                                avail_list[cen['address']] = ses['available_capacity']
                                avail_list_array.append({"Location":cen['address'], "Available":ses['available_capacity'], "pin":cen['pincode']})
                                #subprocess.call("osascript -e '{}'".format(sub), shell=True)
            body_msg = ""
            for each in total_list_array:
                body_msg = body_msg + '{name} -------- {res}-------{pin}\n'.format(name=each['Location'], res=each['Available'], pin=each['pin'])
            print (body_msg)

            if len(avail_list_array) > 0:
                body = '\n\nList of available vaccine location with count and pincode\n'
                for item in avail_list_array:
                    body = body + '{name} -------- {res}-------{pin}\n'.format(name=item['Location'], res=item['Available'], pin=item['pin'])
                print (body)
                send_email("Vaccination available", EMAIL_TO, body )
                #subprocess.call("osascript -e '{}'".format(body), shell=True)
                print ("Vaccine available, mail sent")
            else:
                print ("\n" + 
                str(datetime.now().strftime("%H:%M:%S")) + "\nNo vaccine available.... trying after " + str(frequency) + " seconds\n\n")
                print ("---------------------------------------------------------------")
                body = '\n\nList of available vaccine location with count\n'
                for item in total_list_array:
                    body = body + '{name} - {res}\n'.format(name=item['Location'], res=item['Available'])
                #subprocess.call("osascript -e '{}'".format(body_msg), shell=True)
                #send_email("Vaccination not available in SriGanganagar district", EMAIL_TO, body)
            
        else:
            for eachpin in PINCODE:
                print ("Trying at cowin site at PINCODE :  " + eachpin +  "\nAt ::  " + str(datetime.now().strftime("%H:%M:%S")))
                weburl = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=" + eachpin +  "&date=" + dtime
                r =requests.get(weburl, headers=headers)
                res = r.json()
                centers = res['centers']
                for cen in centers:
                    for ses in cen['sessions']:
                        if ses['min_age_limit'] < 19:
                            print ("Location----------------:     " + cen['address'])
                            print ("available_capacity------:     " + str(ses['available_capacity']))
                            if ses['available_capacity'] > 0:
                                sub = "Covax update: Avaiable at : " + cen['address']
                                send_email(sub, EMAIL_TO)
                                print ("Vaccine available, mail sent")
                                subprocess.call("osascript -e '{}'".format(sub), shell=True)
            print ("\n\nNo vaccine available.... trying after " + str(frequency) + " seconds\n\n")
            print ("---------------------------------------------------------------")
        time.sleep(frequency)
    except Exception as e:
        print ("\n.......  Some exception occured.... continuing.. \n", str(e))
        time.sleep(frequency)
        pass
