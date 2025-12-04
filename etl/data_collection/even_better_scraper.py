from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from time import sleep
import threading
from bs4 import BeautifulSoup

f = open("output.txt", "w")
f.close()

def setup_driver():
    """Initialize and configure the Chrome WebDriver"""
    chrome_options = Options()
    
    # Uncomment the following line to run in headless mode (no browser window)
    # chrome_options.add_argument('--headless')
    
    # Additional options for better stability
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    # Don't use implicit wait when using explicit WebDriverWait
    # driver.implicitly_wait(10)  # Set implicit wait time
    
    return driver

def waitTillLoaded(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

def check_for_captcha(driver):
    """
    Check if the page contains CAPTCHA-related words.
    If found, wait indefinitely while periodically checking until it's resolved.
    """
    captcha_keywords = [
        'captcha', 'recaptcha', 'verify you are human', 'security check',
        'please verify', 'robot', 'automation detected', 'access denied',
        'suspicious activity', 'prove you are human'
    ]
    
    page_text = driver.page_source.lower()
    
    # Check if any captcha keywords are present
    captcha_detected = any(keyword in page_text for keyword in captcha_keywords)
    
    if captcha_detected:
        print("\n" + "="*60)
        print("⚠️  CAPTCHA DETECTED!")
        print("="*60)
        print("Please solve the CAPTCHA in the browser window.")
        print("The script will automatically continue once resolved...")
        print("="*60 + "\n")
        
        # Wait indefinitely, checking every 15 seconds
        while True:
            sleep(15)
            
            # Re-check page content
            page_text = driver.page_source.lower()
            captcha_still_present = any(keyword in page_text for keyword in captcha_keywords)
            
            if not captcha_still_present:
                print("✅ CAPTCHA resolved! Continuing...")
                break
            else:
                print("⏳ Still waiting for CAPTCHA to be solved...")
    
    return not captcha_detected

# Get all the results
def process_data(source, write, allData):
    soup = BeautifulSoup(source, 'html.parser')
    first = soup.select(".appMinimalMenu.viewMenu.appItemSearchResult.noSave.viewInstanceUpdateStackPush")
    second = soup.select(".appMinimalBox.addressSearchResultBox")
    status = soup.select(".appMinimalBox.statusSearchResult")
    registration = soup.select(".appMinimalAttr.RegistrationDate")
    entityType = soup.select(".appMinimalAttr.EntitySubTypeCode")
    for row in range(int(soup.select_one(".appPagerBanner").text.split(" ")[-2])):
        entry = (
            first[row].text,
            second[row].text.replace("\n", ""),
            list(status[row].children)[1].text,
            list(registration[row].children)[1].text,
            list(entityType[row].children)[1].text
        )
        allData.add(entry)

        if write:
            f = open("output.txt", "w")
            # Save progress after entry
            for data in allData:
                f.write("\n".join(data) + "\n\n")
            f.close()



def scrape_businesses(business_type):
    driver = setup_driver()

    # Open website
    driver.get("https://www.appmybizaccount.gov.on.ca/onbis/master/entry.pub?applicationCode=onbis-master&businessService=registerItemSearch")
    waitTillLoaded(driver)
    check_for_captcha(driver)

    # Change the advanced settings
    wait = WebDriverWait(driver, 10)
    advanced_search_link = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Advanced"))
    )
    advanced_search_link.click()
    waitTillLoaded(driver)

    # Set register
    selectOne = Select(wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#SourceAppCode"))
    ))
    selectOne.select_by_index(1)
    waitTillLoaded(driver)
    sleep(0.5)

    # Select business type
    selectE = Select(wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#EntitySubTypeCode"))
    ))
    selectE.select_by_visible_text(business_type)
    waitTillLoaded(driver)


    # Select status
    selectTwo = Select(wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#Status"))
    ))
    selectTwo.select_by_index(1)
    waitTillLoaded(driver)

    allData = set()
    adjustedPageSize = False
    prevThread = None
    alphabet = map(chr, range(65, 91))  # A-Z
    curWord = ["A"]
    itCounter = 0
    autoSave = 10

    # Go through searching all letters A-Z
    while len(curWord) > 0:  # ASCII values for A-Z
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#QueryString"))
        )
        search_input.clear()
        search_input.send_keys("".join(curWord))
        search_input.send_keys(Keys.RETURN)

        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.ID, "catProcessing"))
        )
        
        # Check for CAPTCHA after search
        check_for_captcha(driver)

        # Adjust page size to 200 if not already done
        if not adjustedPageSize:
            try:
                # The ID might change (W807, W873, etc.), so use partial match
                selectPageSize = Select(WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[id*='PageSize']"))
                ))
                # Select by value "4" which corresponds to 200 items
                selectPageSize.select_by_value("4")
                WebDriverWait(driver, 60).until(
                    EC.invisibility_of_element_located((By.ID, "catProcessing"))
                )
                adjustedPageSize = True
            except Exception as e:
                print(f"Could not adjust page size: {e}")
                adjustedPageSize = True

        # If there are more than 200 results, refine search
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "appSearchResultsTitle"))
        )
        noEntry = False
        try:
            if int(driver.find_element(By.CLASS_NAME, "appPagerBanner").text.split(" ")[-2]) >= 200:
                curWord.append('A')
                continue
        except:
            noEntry = True
            print("No results found for " + "".join(curWord))
        
        if prevThread is not None:
            prevThread.join()

        if not noEntry:
            itCounter += 1

            prevThread = threading.Thread(target=process_data, args=(driver.page_source, itCounter>=autoSave, allData))
            prevThread.start()

            if itCounter >= autoSave:
                itCounter = 0

        # Adjust the current search word
        while len(curWord) > 0:
            if curWord[-1] == 'Z':
                curWord.pop()
            else:
                curWord[-1] = chr(ord(curWord[-1]) + 1)
                break

    # Final save with all data sorted and removed duplicates
    with open("output.txt", "w") as f:
        for data in sorted(allData):
            f.write("\n".join(data) + "\n\n")
    driver.quit()

def main():
    """Main function to run all scrapers concurrently."""
    # Create threads for each business type
    thread1 = threading.Thread(target=scrape_businesses, args=("Not-for-Profit Corporation",))
    thread2 = threading.Thread(target=scrape_businesses, args=("Co-operative with Share",))
    thread3 = threading.Thread(target=scrape_businesses, args=("Co-operative Non-Share",))
    
    # Start all threads
    print("Starting concurrent scraping...")
    thread1.start()
    sleep(2)  # Stagger starts slightly to avoid resource conflicts
    thread2.start()
    sleep(2)
    thread3.start()
    
    # Wait for all threads to complete
    print("Waiting for all scrapers to finish...")
    thread1.join()
    thread2.join()
    thread3.join()
    
    print("All scraping complete!")

if __name__ == "__main__":
    main()