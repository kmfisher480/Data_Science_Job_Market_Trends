# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 15:48:02 2024

@author: KatieFisher
"""

import requests
import json
import time


#NOTE: replace 'xxxxx' with your own info!

# Define the URL and other fixed parameters
url = "https://api.scrapingdog.com/linkedinjobs/"
api_key = "xxxxx" #enter you API ckey from scraping dog when you sign up, they give you a 30day free trial!
field = "Data Scientist" #replace with Data Analyst Either (or whatever!)
geoid = "100025096" #This is Torontto but you can find this by looking at the url of a specific job posting on linkedin in your desired location
sort_by = "month"  # Looks at jobs posted in the last month


# List to store all jobs
all_jobs = []

#the api requests you put in a page number but I want the last 150 jobs
#assumes 10 jobs per page - you can check this by just running 1 page 
number_jobs = 500
jobs_per_page = 10
page_number_max = int(number_jobs / jobs_per_page) +1 #adding one so the loop is corect

for page in range(1, page_number_max):
    # Update the parameters for each page
    params = {
        "api_key": api_key,
        "field": field,
        "geoid": geoid,
        "page": str(page),
        "sort_by": sort_by  # Add this to sort by posting date (month/week/day)
    }
    
    # track retries
    retries = 3

    while retries > 0:
        # Send a GET request with the parameters
        response = requests.get(url, params=params)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Access the response content and print the data structure
            data = response.json()
            print(f"Page {page}: Response structure type is {type(data)}")
            # If the response is a list, extend the all_jobs list with it
            if isinstance(data, list):
                num_jobs = len(data)
                print(f"Page {page}: Found {num_jobs} jobs")
                all_jobs.extend(data)  # Assuming the data is a list of jobs
            break  # Exit the retry loop if successful
        else:
            print(f"Request failed on page {page} with status code: {response.status_code}")
            retries -= 1
            time.sleep(2)  # Wait before retrying

    if retries == 0:
        print(f"Skipping page {page} after multiple attempts.")

# Save the job data to a JSON file
with open('all_data_scientist_jobs.json', 'w') as json_file:
    json.dump(all_jobs, json_file, indent=4)

print(f"Total jobs found: {len(all_jobs)}/{number_jobs}")
print("Job data saved to all_data_scientist_jobs_simple.json")
