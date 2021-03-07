## Wristband Project ##

This is a Python-based webapp for users to access a subset of Dojo operations, particularly the ones related to wristband registrations and manual scan in of ninjas.

### Requirements to Run the Web App ###
* Python 3.x

### First Time Setup ###
After cloning or downloading the zip file, go to this project folder and create a Python virtual environment:

    $ python3 -m venv venv

This will create a directory `venv` under the project directory.  To activate this:

    $ source venv/bin/activate

This command lets us enter the virtual environment, and the command prompt should have some indication that we are in, something like `(venv)` as the prefix.

For the first time, we should install all required dependencies using this command:

    (venv) $ pip install --upgrade pip
    (venv) $ pip install -r requirements.txt

That should do it.  The next time around you want to run the webapp.py, there's no need to do all these installs, just enter the virtual environment prior to running the web app using the `source venv/bin/activate` command.

### Running the Web Application ###
From the command prompt, simply run:

    (venv) $ python webapp.py



The app will then ask 4 questions:
* **Location Slug**, this is simply your Code Ninjas location id.  Example: `cn-ca-rocklin` for Rocklin, CA.
* **Code Ninjas Account Email Address**, this will be the Microsoft Exchange email address.
* **Password**, the password, of course.
* **Complete path to the wristband mapping JSON file**, this can be any file on your file system as long as it has read/write access.  This file will contain an RFID mapping for the duds management.

After answering those 4 questions, the app will go ahead and login to the Dojo and when it's logged in, it will print the web cookies and the following lines to indicate it is up:

    * Serving Flask app "webapp" (lazy loading)
    * Environment: production
      WARNING: This is a development server. Do not use it in a production deployment.
      Use a production WSGI server instead.
    * Debug mode: off

Now you can open your web browser and access it: http://localhost:5000 ...

## Features
### Manual Scan-In ###
The webapp displays the list of active ninjas.  To sign a ninja in manually into the Dojo, you can just click the **Manual Scan-In** button.

If the ninja is a JR ninja, no active wristband is required and you can just sign the ninja in for a JR session.

If the ninja is a CREATE ninja, an active wristband is needed.  If no active wristband is found, an error message should show up indicating so.  If the ninja already has the active wristband, then this ninjas can then sign in for 1-hour or 2-hour session.

### Register a Virtual Wristband ###
Since a CREATE ninja needs an active wristband to sign in, one can create an imaginary wristband (after all, the wristband is just carrying an 8-digit hexadecimal ID).

If you don't have a physical wristband to assign/register for the new ninja, you can always register them a virtual wristband so that they can still sign in to the dojo.

To do this, locate your ninja on the web app and click the **Manage Wristband** button.  Then click **Register Virtual Wristband**.

If successful, then this new ninja can be scanned in manually and have Dojo access.

If failed, then that should be an anomaly and it just happens that the random ID hits a match of an ID that is already used before, ... very unlikely, but can happen.  Just try again.

**Note:** This pretty much means that if you don't really care about giving away wristbands to your ninjas, you can still have them sign in by means of virtual wristbands.

### Register a Physical Wristband ###
This is the same feature as what's in our official Dojo to register wristband, but it has an additional feature when dealing with duds.

Locate your ninja for whom you want to register a wristband, click the **Manage Wristband** button, then place the cursor to the **Wristband RFID** text box and scan the wristband, it should then write something along the lines of `;12ab34cd?`, for example.  That is the RFID value, if it has exactly 8 hexadecimal digits, then you can click the **Register Physical Wristband** button.

If the program detects that it is good the first time around, then great, we don't need any additional action.  Give that good wristband to the ninja and we're good, as if we're doing it on the official Dojo website.

If the program detects an error, then we're potentially dealing with a dud.  The program, under the covers, will do this:
* Assign a virtual wristband for this ninja and register it, in the account that this fails, then it is a rare anomaly that the random ID actually matches something that's already registered in the Dojo.  This should be very rare, try again after seeing the error message.
* Map the Physical Wristband ID that was scanned to this new random virtual wristband ID and save it to the mapping file.

### Scan Wristband ###
Although by now we can register a dud wristband by means of mapping it to a virtual wristband ID, the official Ninja Wristband Scan In will not be able to understand your dud wristband.

For that, we have a simplistic **Scan Wristband** button at the top of the web app.  Click it, and place the cursor in the Wristband RFID text box and scan the wristband.  And click **Check Wristband**.

If the wristband RFID is recognized, then it should proceed with the same scan in option for the matched ninja.
