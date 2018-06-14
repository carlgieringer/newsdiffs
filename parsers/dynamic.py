import os
import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chromedrivers'))
if platform.system() == 'Linux':
    chrome_driver_path = os.path.join(driver_dir, "chromedriver_linux64")
elif platform.system() == 'Darwin':
    chrome_driver_path = os.path.join(driver_dir, "chromedriver_mac64")
elif platform.system() == 'Windows':
    chrome_driver_path = os.path.join(driver_dir, "chromedriver_win32.exe")
else:
    raise RuntimeError('Unsupported platform.system: ' + platform.system())
# driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)
service = webdriver.chrome.service.Service(chrome_driver_path)
service.start()

# chrome_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'

def grab_url_dynamic(url):
    driver = webdriver.Remote(service.service_url, desired_capabilities=chrome_options.to_capabilities())
    driver.get(url)
    return driver.page_source
