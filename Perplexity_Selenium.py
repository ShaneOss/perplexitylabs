from time import sleep
from uuid import uuid4
from random import getrandbits
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from time import time
import json
import logging

from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
from seleniumwire import webdriver
from seleniumwire.utils import decode

seleniumwire_logger = logging.getLogger('seleniumwire')
seleniumwire_logger.setLevel(logging.ERROR)

webdriver_logger = logging.getLogger('selenium.webdriver')
webdriver_logger.setLevel(logging.ERROR)

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Perplexity:
    """A class to interact with the Perplexity website.
    To get started, you need to create an instance of this class.
    For now, this class only supports one answer at a time.
    """
    def __init__(self):
        # Initialize a random user agent
        ua = UserAgent()
        self.user_agent = ua.random

        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument(f'--user-agent={self.user_agent}')
        options.add_argument("--headless=new")  # for hidden mode
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,955")

        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(options=options)
        
        self.searching = False

        self.query_str = ""
        self.answer = ""
        self.tokens = ""

        # Available Models
        # codellama-34b-instruct
        # llama-2-7b-chat
        # llama-2-13b-chat
        # llama-2-70b-chat
        self.model = "llama-2-13b-chat"
        self.init_main()
        

    def init_main(self):
        # Open the Perplexity website
        self.driver.get("https://labs.perplexity.ai")
    
        try:
            # Wait for the dropdown element to be visible
            wait = WebDriverWait(self.driver, 10)
            modelselect = wait.until(EC.visibility_of_element_located((By.ID, 'lamma-select')))

            # Click on the dropdown to open it
            modelselect.click()
            
            # Select an option from the dropdown by its text
            option_text = self.model
            option = self.driver.find_element(By.XPATH, f"//option[text()='{option_text}']")
            option.click()

        except Exception as e:
            print(f"Error: {e}")
        
        #self.driver.save_screenshot('perplexity_model_selected.png')

    def search(self, query: str, retry_count=0):
        self.driver.get("https://labs.perplexity.ai")
        self.searching = True
        formatted_query = query.replace('\n', '\\n').replace('\t', '\\t')
        self.query_str = formatted_query
                
        # Count the number of characters
        #character_count = len(self.query_str)
        #if character_count > 2000:
        #    return "Input string is greater than 2000 character limit."
        
        # Wait for the textarea element to be visible
        wait = WebDriverWait(self.driver, 10)
        textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'textarea')))

        # Click on the textarea to focus on it
        textarea.click()
        
        # Send text to the textarea
        for part in self.query_str.split('\\n'):
            textarea.send_keys(part)
            ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        
        # Wait for JavaScript to process the text input
        sleep(4)       
       
        # Wait for the button element to be clickable
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'bg-super')]")))

        # Click on the button
        button.click()
        
        #self.driver.save_screenshot('perplexity_message_request.png')
                
        response = ""

        self.error = False
        while (not self.error) and ('"status":"completed"' not in response) and ('"final":true' not in response or '"status":"failed"' not in response):
            for request in self.driver.requests:
                if "https://labs-api.perplexity.ai/socket.io/?EIO=4&transport=polling&t=" in request.url:
                    #print(request.url)
                    if request.response is not None:
                        data = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                        data = data.decode("utf8")
                        response = data
                        #print(response)
                if response.startswith(f"42[\"{self.model}_query_progress") and '"status":"' in response:
                    # Split the response by "42["llama-2-13b-chat_query_progress"," to separate the JSON objects
                    json_objects = response.split(f'42["{self.model}_query_progress",')

                    # Iterate through each JSON object and parse it
                    data = []
                    for json_str in json_objects:
                        if json_str != "":
                            json_str = json_str.rstrip()
                            json_str = json_str[:json_str.rfind(']')].rstrip()
                            #print("JSON: ", json_str)
                            data = json.loads(json_str)

                    if "final" in data and data["final"] == True:
                                # Check if "output" exists in the data
                                if "output" in data:
                                    self.answer = data["output"].strip()
                                    #If you need the token count...
                                    self.tokens = data["tokens_streamed"]
                                    self.searching = False
                                    break
                    elif "status" in data and data["status"] == "failed":
                        self.searching = False
                        print(data["text"])
                        self.error = True
                        break                    
            sleep(1)
        
        #self.driver.save_screenshot('perplexity_message_response.png')
        
        if self.answer != "":
            formatted_output = self.answer.replace('\\n', '\n').replace('\\t', '\t')
            return formatted_output
        else:
            self.searching = False       
        
        self.driver.quit()
