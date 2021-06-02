import argparse
import configparser
import getpass
import random

from flask import Flask, json, request, render_template, send_from_directory
from helper.dojo import Dojo
from helper.wristbandmapping import WristbandMapping

app = Flask(__name__)
app.config.from_object(__name__)

dojo = None
wristband_mapping = None
location_slug, email, password = None, None, None

def generate_rfid():
    random.seed()
    return ''.join(map(lambda x: "0123456789abcdef"[random.randrange(0, 16)], range(6))) + '04'

@app.route('/')
def root():
    return render_template("index.html")

@app.route('/scan-in')
def scan_in():
    return render_template("scan-in.html")

@app.route('/api/ninjas')
def get_ninjas():
    url = 'https://dojo.code.ninja/api/reports/{}/activesubscriptions'.format(location_slug)
    resp = dojo.get_json(url, method="POST")
    json_data = resp.json()['values']
    if resp.status_code == 200:
        return json.dumps(json_data)
    else:
        return json.dumps({}), 500

@app.route('/api/wristbands')
def get_ninja_by_rfid():
    args = request.args
    if 'rfid' in args:
        rfid = args['rfid']
        rfid = wristband_mapping.get(rfid)
        url = 'https://dojo.code.ninja/api/employee/{}/students?rfid={}'.format(location_slug, rfid)
        resp = dojo.get_json(url)
        json_data = resp.json()
        return json.dumps(json_data)
    else:
        return json.dumps({}), 404

@app.route('/api/ninjas/<guid>/registerWristband', methods=['POST'])
def action_register_wristband(guid):
    data = request.get_json(force=True)
    for arg_name in ['isVirtual', 'rfid']:
        if not arg_name in data:
            return json.dumps({ 'message': 'Missing argument: {}'.format(arg_name)}), 500

    is_virtual = data['isVirtual']
    rfid = data['rfid']

    del data['isVirtual']

    url = 'https://dojo.code.ninja/api/students/{}/wristband'.format(location_slug)
    data['studentGuid'] = guid
    data['slug'] = location_slug
    print('Register wristband data: {}'.format(data))
    resp = dojo.get_json(url, method='POST', data=data)
    if resp.status_code == 200 and resp.json()['successful']:
        print('Successful at the first try, no need to save any mapping data')
        return json.dumps(resp.json()), 200

    if not is_virtual:
        # This is likely the so-called dud, registration fails for whatever reason.
        # We will simply create a random RFID and assign the mapping.
        wristband_rfid = rfid
        rfid = generate_rfid()
        data['rfid'] = rfid
        print('Register mapped wristband data: {}'.format(data))
        resp = dojo.get_json(url, method='POST', data=data)
        if resp.status_code == 200 and resp.json()['successful']:
            print('Successfully registered a mapped wristband, wristband RFID: {}, registered RFID: {}'.format(wristband_rfid, rfid))
            wristband_mapping.create(wristband_rfid, rfid)
        else:
            print('Unable to register a random RFID for mapping, user should try again.')
        return json.dumps(resp.json()), resp.status_code

@app.route('/api/ninjas/<guid>')
def get_ninja_detail(guid):
    url = 'https://dojo.code.ninja/api/customerdetailsstudent/{}/studentoverview/{}'.format(location_slug, guid)
    resp = dojo.get_json(url)
    return json.dumps(resp.json()), resp.status_code

@app.route('/api/ninjas/<guid>/login', methods=['POST'])
def action_ninja_login(guid):
    data = request.get_json(force=True)
    for arg_name in ['length', 'programCode', 'licenseGuid']:
        if not arg_name in data:
            return json.dumps({ 'message': 'Missing argument: {}'.format(arg_name)}), 500
    sign_in_type = 'recordathomescanin' if data['programCode'] == 'JR' else 'recordmanualscanin'
    url = 'https://dojo.code.ninja/api/employee/{}/{}/{}?licenseId={}&length={}'.format(location_slug, sign_in_type, guid, data['licenseGuid'], data['length'])
    resp = dojo.get_json(url, method='POST')
    return resp.json(), resp.status_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", dest="port", help="Port to listen to", default=5000)
    parser.add_argument("--location", "-l", dest="location", help="Location slug to use", default='')
    parser.add_argument("--cn-email", "-E", dest="cn_email", help="Email to use", default='')
    parser.add_argument("--wristband-mapping", "-M", dest="wristband_mapping", help="Wristband mapping file to use", default='')
    args = parser.parse_args()

    system_config = configparser.ConfigParser()
    system_config.read('webapp.config.ini')
    config = system_config['DEFAULT']

    location_slug = args.location or config['location'] or input('Location Slug: ').strip()
    email = args.cn_email or config['email'] or input('Code Ninjas Account Email Address: ').strip()
    password = config['password'] or input('Password: ')
    wristband_mapping_file = args.wristband_mapping or config['wristbandMappingFile'] or input('Full path to wristband mapping JSON file: ').strip()

    wristband_mapping = WristbandMapping(wristband_mapping_file)

    dojo = Dojo(location_slug, email, password)
    dojo.login()

    app.run(port=args.port)
