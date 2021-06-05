# covax availablity check and notification based on PINCODE
1. Install Python3.6 or higher
2. Install requests module if not by PIP 
  2.1 for windows - https://phoenixnap.com/kb/install-pip-windows
  2.3 for linux/mac - https://www.geeksforgeeks.org/how-to-install-pip-in-macos/
3. Update data.yaml file with PINCODE to search for in 'search_in', PINCODE to exclude in 'exclude
4. Update data.yaml file with frequency "how frequent script need to check vaccine availablity" under frequency variable in seconds
5. Update district id code in 'district_id' variable, get district code from below step as "To get list of distrct ID"
6. Update variable 'EMAIL_TO' to who to send email notification once vaccine available
7. Update variable 'EMAIL_FROM' to send email
8. Run script, as below
python3.7 abc.py -u "xyz@gmail.com" -p "xyzpassword"

Note: Only gmail account supported to run script. Pleasee allow gmail setting to allow less secured app as ON. Make sure to revert it back once you do not wish to run this script.

To get list of distrct ID:
1. In browser put url: https://cdn-api.co-vin.in/api/v2/admin/location/states
2. get state id and append in this url: https://cdn-api.co-vin.in/api/v2/admin/location/districts/<state_id>
e.g https://cdn-api.co-vin.in/api/v2/admin/location/districts/29 --> will show all district of Rajasthan, state_id is 29

Be relax script will keep on checking vaccine availablity status based on frequency set. 
