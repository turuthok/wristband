import json
import requests
import chromedriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

class Dojo:
  def __init__(self, location_slug, email, password):
    self.location_slug = location_slug
    self.email = email
    self.password = password
    self.cookies = {}

  def get_cookies_for_dojo_access(self, cookies):
    res = []
    for cookie in cookies:
      if cookie['name'].startswith(".AspNet"):
        res.append("{}={}".format(cookie['name'], cookie['value']))
    return '; '.join(res)

  def do_request(self, url, method, headers, data):
    if method == 'GET':
      resp = requests.get(url, headers=headers)
    elif method == 'PUT':
      if data:
        resp = requests.put(url, headers=headers, json=data)
      else:
        resp = requests.put(url, headers=headers)
    elif method == 'POST':
      if data:
        resp = requests.post(url, headers=headers, json=data)
      else:
        resp = requests.post(url, headers=headers)
    else:
      return None
    return resp

  def get_json(self, url, method='GET', data=None):
    # We will do at most two attempts, if the first time around fails with authentication problem,
    # we should try by re-logging in to the Dojo.  On the second attempt, if it still fails, we'll just
    # return the response however it may look like.
    # If the first attempt returns without authentication problem, we will just return it however it may
    # look like.
    resp = None
    for iter in range(2):
      headers = {}
      if self.cookies:
        headers['cookie'] = self.get_cookies_for_dojo_access(self.cookies)

      resp = self.do_request(url, method, headers, data)
      if resp is None:
        break

      if iter == 0 and (resp.status_code == 401 or resp.status_code == 403):
        # This is the first attempt, and it's unauthorized, let's login.
        if not self.login():
          # Login failed, so we'll just give up, otherwise, it will just continue to do the second attempt.
          break
      else:
        break
    return resp

  def login(self):
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--incognito")

    chromedriver_autoinstaller.install()

    driver = webdriver.Chrome(options=options)
    driver.get("https://dojo.code.ninja/employees/{}".format(self.location_slug))

    steps = [
      ("Microsoft 365 Exchange", "click", "CodeNinjasExchange", None),
      ("Enter username", "text", "i0116", self.email),
      ("Enter password", "text", "i0118", self.password),
      ("Submit without saving info", "click", "idBtn_Back", None),
      ("Check successful login", "title", "Dashboard - Code Ninjas Dojo", None)
    ]

    for desc, action, id, keys in steps:
      ec = None
      if action == "click":
        ec = expected_conditions.element_to_be_clickable((By.ID, id))
      elif action == "text" or action == "check":
        ec = expected_conditions.visibility_of_element_located((By.ID, id))
      elif action == "title":
        ec = expected_conditions.title_is(id)

      element = None
      try:
        element = WebDriverWait(driver, 10).until(ec)
      except TimeoutException:
        return False

      if action == "click":
        element.click()
      elif action == "text":
        element.send_keys(keys)
        element.send_keys(Keys.ENTER)

    self.cookies = driver.get_cookies()
    print("Cookies: {}".format(self.cookies))

    driver.quit()

