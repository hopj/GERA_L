#import mechanicalsoup
import re
from robobrowser import RoboBrowser
#import config

browser = RoboBrowser()
browser.open("https://github.com/login")

# Get the signup form
#signup_form = browser.get_form(class_='auth-form-body mt-3')
form = browser.get_form()
form["login"].value = "hopj"  #config.GITHUB["USER"]
form["password"].value = "4fates6e" #config.GITHUB["PASS"]
browser.submit_form(form)

for tag in browser.find_all("a"): 
    if "GERA_L" in tag['href'] :
        print(tag['href'])

