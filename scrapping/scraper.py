import time
import pandas as pd

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import bs4
import os


URL = "https://www.google.com/maps/place/Puskesmas+Keputih/@-7.2940487,112.8017864,17z/data=!3m1!4b1!4m6!3m5!1s0x2dd7fa707ffe8e9b:0x48ba1072a2457fc2!8m2!3d-7.2940487!4d112.8017864!16s%2Fg%2F1hm3zzsvs"
DATA_NAME = "Puskesmas Keputih"


def scrape_reviews(url, data_name, save_dir):
    """
    Scrape reviews from Google Maps and save it to a csv file.
    """
    data = pd.DataFrame(columns=["reviewer_name", "rating", "review_text"])

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)

    time.sleep(1)

    review_button = driver.find_element(
        By.XPATH, "//button[@class='hh2c6 ' and @data-tab-index='1']"
    )
    review_button.click()

    time.sleep(2)

    scrollable_div = driver.find_element(
        By.XPATH, "//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']"
    )
    curr_scroll_pos = 0
    while True:
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div
        )
        time.sleep(1)
        new_scroll_pos = driver.execute_script(
            "return arguments[0].scrollTop", scrollable_div
        )
        if new_scroll_pos == curr_scroll_pos:
            break

        curr_scroll_pos = new_scroll_pos

    more_buttons = driver.find_elements(By.XPATH, "//button[@class='w8nwRe kyuRq']")
    for button in more_buttons:
        try:
            button.click()
            time.sleep(1)
        except:
            pass

    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    container = soup.find_all(
        "div", attrs={"data-review-id": True, "aria-label": True, "jslog": True}
    )

    for review in container:
        reviewer_name = None
        rating = None
        review_text = None
        try:
            reviewer_name = review["aria-label"]
            rating = review.find("span", class_="kvMYJc").get("aria-label")
            review_text = review.find("span", class_="wiI7pd").text
        except:
            pass

        temp_data = pd.DataFrame(
            {
                "reviewer_name": [reviewer_name],
                "rating": [rating],
                "review_text": [review_text],
            }
        )
        data = pd.concat([data, temp_data], ignore_index=True)

    os.makedirs(save_dir, exist_ok=True)
    data.to_csv(f"{save_dir}/review_{data_name}.csv", index=False)

    driver.quit()


if __name__ == "__main__":
    scrape_reviews(URL, DATA_NAME, "scrapped")
