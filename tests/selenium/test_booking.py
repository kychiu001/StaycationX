# Must consult the table in https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html 
# to identify compatible versions of geckodriver and Firefox
# In my wsl, I use the top line of the table, which is geckodriver v0.33.0 and Firefox > 102 ESR

# Ref: https://www.rickmakes.com/windows-subsystem-for-linux-2-installing-vcxrv-x-server/
# Add the following to ~/.bashrc
# export DISPLAY=172.18.144.1:0.0
# export LIBGL_ALWAYS_INDIRECT=1
# also need to set DNS in /etc/resolv.conf
# echo -e "nameserver 172.18.144.1\nnameserver 8.8.8.8\nnameserver 8.8.4.4" | sudo tee /etc/resolv.conf
# where 172.18.144.1 is the ip address of the WSL host by doing ipconfig in cmd.exe

# Also to make XcXsrv X server start automatically 
# by moving config file /d/tars/config.xlaunch to %APPDATA%\roaming\Microsoft\Windows\Start Menu\Programs\Startup 
# config.xlaunch is configured by starting Xlaunch and saving the config file

# When run by it by pytest, you can first set PYTHONPATH to the root of the project
# export PYTHONPATH=/d/tars/staycationX or export PYTHONPATH="${PYTHONPATH}:."
# Then run: pytest -s -v tests/selenium/test_booking.py
# Or: MOZ_HEADLESS=1 pytest -s -v tests/selenium/test_booking.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import os

def test_booking():
    service_obj = Service("/d/tars/geckodriver")

    # added for headless 
    options = FirefoxOptions()
    # options.headless = True

    # To run headless firefox, need to set MOZ_HEADLESS environment variable to 1
    # Configure launch.json with the following statement
    # {
    #        "type": "python",
    #        "request": "launch",
    #        "name": "pytest",
    #        "module": "pytest",
    #        "env": {
    #          "MOZ_HEADLESS":"1"
    #        }
    # }
    # And use the debug in VSCode to run pytest
    
    if os.getenv('MOZ_HEADLESS') == '1':
        options.add_argument("--headless")  
        options.add_argument("--window-size=1920x1080") 

    driver = webdriver.Firefox(service=service_obj, options=options)

    driver.maximize_window()
    driver.get("localhost:5000")

    driver.find_element(By.XPATH,"//a[@href='/viewPackageDetail/Shangri-La Singapore']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "(//a[normalize-space()='Back to Packages'])[1]").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//a[normalize-space()='Login']").click()
    driver.find_element(By.CSS_SELECTOR, "#email").send_keys("peter@cde.com")
    driver.find_element(By.CSS_SELECTOR, "#pwd").send_keys("12345")
    driver.find_element(By.CSS_SELECTOR, "button[value='login']").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '''.btn.btn-primary[href="/view?hotel_name='Shangri-La Singapore'"]''').click()

    print("Application Title: ", driver.title)
    print("Application URL: ", driver.current_url)
    # driver.quit()