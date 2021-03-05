import argparse
import getpass

from flask import Flask, json, request
from helper.dojo import Dojo

app = Flask(__name__)
app.config.from_object(__name__)

dojo = None

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--chromedriver", dest="chromedriver", help="Path to chromedriver", default="/usr/local/bin/chromedriver")
  args = parser.parse_args()

  location_slug = input("Location Slug: ").strip()
  email = input("Code Ninjas Account Email Address: ").strip()
  password = getpass.getpass("Password: ")

  dojo = Dojo(location_slug, email, password, args.chromedriver)
  dojo.login()

