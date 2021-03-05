import argparse
import getpass

from flask import Flask, json, request, render_template, send_from_directory
from helper.dojo import Dojo

app = Flask(__name__)
app.config.from_object(__name__)

dojo = None
location_slug, email, password = None, None, None

@app.route('/')
def root():
  return render_template("index.html")

@app.route('/api/ninjas')
def get_ninjas():
  args = request.args
  if 'rfid' in args:
    rfid = args['rfid']
    url = 'https://dojo.code.ninja/api/employee/{}/students?rfid={}'.format(location_slug, rfid)
    resp = dojo.get_json(url)
    json_data = resp.json()
  else:
    url = 'https://dojo.code.ninja/api/reports/{}/activesubscriptions'.format(location_slug)
    resp = dojo.get_json(url, method="POST")
    json_data = resp.json()['values']
  if resp.status_code == 200:
    return json.dumps(json_data)
  else:
    return json.dumps({}), 500

@app.route('/api/ninjas/<guid>')
def get_ninja_detail(guid):
  url = 'https://dojo.code.ninja/api/customerdetailsstudent/{}/studentoverview/{}'.format(location_slug, guid)
  resp = dojo.get_json(url)
  return json.dumps(resp.json()), resp.status_code

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--chromedriver", dest="chromedriver", help="Path to chromedriver", default="/usr/local/bin/chromedriver")
  args = parser.parse_args()

  location_slug = input("Location Slug: ").strip()
  email = input("Code Ninjas Account Email Address: ").strip()
  password = getpass.getpass("Password: ")

  dojo = Dojo(location_slug, email, password, args.chromedriver)
  dojo.login()

  app.run(debug=True)

