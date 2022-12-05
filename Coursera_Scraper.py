from concurrent.futures import thread
from selenium.webdriver.common.keys import Keys
from time import thread_time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import pymongo
import pandas as pd

# setup connection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["coursera_data"]


# 2. Write code to create a collection ‘movies’, and add 5 movies to the database that you 
# last watched, having property: name, genre, rating.
collection = mydb["coursera_data"]
course_list = []

options = Options()
options.headless = False
driver = webdriver.Chrome("C:/Users/vinay/Downloads/chromedriver_win32/chromedriver.exe",options=options)
# driver = webdriver.PhantomJS("C:/Users/vinay/Downloads/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe")
# driver.maximize_window()
# courseToSearch = "machinelearning"
# url = "https://www.coursera.org/search?query="+courseToSearch
import time

url = "https://www.coursera.org/search?page="+str(1)+"&index=prod_all_launched_products_term_optimization"
driver.get(url)
time.sleep(5)
for pageindex in range (31,85):
    

    # driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
    # driver.find_element_by_id("search_button_homepage").click()
    # driver.find_element_by_xpath("//input[@placeholder='What do you want to learn?']").send_keys("Machine learning")
    # driver.find_element_by_xpath("//input[@placeholder='What do you want to learn?']").send_keys(Keys.ENTER)
    # driver.find_element_by_xpath("//button[@aria-label='Submit Search'][@class='nostyle search-button']").click()
    
    
    
    # driver.refresh()
   
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@data-click-key='search.search.click.search_card']")))
    # WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".reply-button"))).click()


    search_results = driver.find_elements(By.XPATH,"//a[@data-click-key='search.search.click.search_card']") 
    print(pageindex)
    provider_index = 1
    rating_index = 1
    review_index = 1
    proficiency_index = 1
    skill_index = 1
    lvl_index = 2
    count = 1
    print(driver.current_url)
    for element in search_results:
        #course name
        # course_name = element.get_attribute("aria-label")
       
        # print(course_name)
        xPath = "(//a[@data-click-key='search.search.click.search_card']//descendant::h2)["+str(count)+"]"
        course_name =element.find_element_by_xpath(xPath).text
        count+=1
        print(course_name)

        #course link
        course_link = element.get_attribute("href")
        # print(course_link)

        # xpath for provider
        xPath = "(//a[@data-click-key='search.search.click.search_card']//descendant::span)["+str(provider_index)+"]"
        course_provider =  element.find_element_by_xpath(xPath).text
        # print(course_provider)
        provider_index+=2

        # Xpath for rating
        if "reviews)" not in element.text:
            print ("no review")
            course_reviews = 0
            # rating_index-=1
        else:
            xPath = "(//a[@data-click-key='search.search.click.search_card']//descendant::div[@class='css-pn23ng']/p[1])["+str(rating_index)+"]"
            course_ratings =  element.find_element_by_xpath(xPath).text
            if "Coursera Plus" in course_ratings:
                rating_index+=1
                xPath = "(//a[@data-click-key='search.search.click.search_card']//descendant::div[@class='css-pn23ng']/p[1])["+str(rating_index)+"]"
                course_ratings =  element.find_element_by_xpath(xPath).text
            rating_index+=1
        # print(course_ratings)

        if "reviews)" not in element.text:
            print ("no review")
            course_reviews = 0
            review_index-=1
        # Xpath for review
        else:
            xPath = "(//a[@data-click-key='search.search.click.search_card']//descendant::div[@class='css-pn23ng']/p[2])["+str(review_index)+"]"
            course_reviews =  element.find_element_by_xpath(xPath).text
            course_reviews = course_reviews.replace("(","").replace("reviews","").replace(")","").strip()
            if "k" in course_reviews:
                course_reviews = float(course_reviews.replace("k","")) * 1000
            review_index+=1
        # print(course_reviews)

    
        # Xpath for skills
        if "Skills you" in element.text:
            xPath = "(//*[contains(text(),'Skills you')]/../..)["+str(skill_index)+"]"
            course_skills =  element.find_element_by_xpath(xPath).text
            course_skills = course_skills.split(":")[1].strip()
            skill_index+=1
        else:
            course_skills =""
            provider_index-=1 # reduced as missing skills section reduces the element index for provider
        # print(course_skills)

        #Xpath for proficiency
        xPath = "(//a[@data-click-key='search.search.click.search_card']//p[contains(text(),'Month') or contains(text(),'Weeks') or contains(text(),'Hours') or contains(text(),'Days')])["+str(proficiency_index)+"]"
        #  xPath = "(//a[@data-click-key='search.search.click.search_card']//descendant::p[@class='cds-33 css-14d8ngk cds-35' and not(contains(@data-e2e,'creditEligibleText'))][2])["+str(review_index)+"]"
        course_proficiency =  element.find_element_by_xpath(xPath).text
        lvl = course_proficiency.replace("Credit Eligible","").split(" ")[0].strip()
        # print(lvl)
        proficiency_index +=1
        # print("=========================================\n")
        course_list.append({
            "course_name":course_name,
            "course_link":course_link,
            "course_provider":course_provider,
            "course_skills":course_skills,
            "course_ratings":course_ratings,
            "course_reviews":course_reviews,
            "course_proficiency":lvl

        })

    try:
        next_button = driver.find_element_by_xpath("//button[@aria-label='Next Page']")
        next_button.click()
        time.sleep(5)
    except:
        print("none")

    if pageindex % 10 == 0:
        x = collection.insert_many(course_list)
        course_list = []
        
        


# print(driver.current_url)
x = collection.insert_many(course_list)
driver.quit()
