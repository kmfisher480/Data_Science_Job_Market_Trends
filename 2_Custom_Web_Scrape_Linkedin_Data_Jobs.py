import os
import json
import random
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import logging


#NOTE: replace 'xxxxx' with your own info!

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO)

# Load job listings from the JSON file
with open('all_data_analyst_jobs.json', 'r') as json_file:
    job_data = json.load(json_file)

# List to store job descriptions and applicant counts
job_descriptions = []

# Set up Selenium WebDriver
chromedriver_path = r'C:\Users\xxxxx\chromedriver-win64\chromedriver-win64\chromedriver.exe' #enter path to your chromer driver - should look something like this but replace xxxxx
service = Service(chromedriver_path)
chrome_options = Options()
driver = webdriver.Chrome(service=service, options=chrome_options)
os.environ['LINKEDIN_EMAIL'] = 'xxxxx' #enter your email log in for linkedin
os.environ['LINKEDIN_PASSWORD'] = 'xxxxx!' #enter your pass word for linked

try:
    # Log in to LinkedIn
    driver.get('https://www.linkedin.com/login')
    time.sleep(3)
    # Retrieve LinkedIn credentials from environment variables
    linkedin_email = os.getenv('LINKEDIN_EMAIL')
    linkedin_password = os.getenv('LINKEDIN_PASSWORD')
    
    # Ensure that the variables are not None
    if linkedin_email is None or linkedin_password is None:
        raise ValueError("LinkedIn email or password environment variables not set")
    
    # Enter your LinkedIn email and password
    email_element = driver.find_element(By.ID, 'username')
    email_element.send_keys(linkedin_email)  # Use environment variable for email
    
    password_element = driver.find_element(By.ID, 'password')
    password_element.send_keys(linkedin_password)  # Use environment variable for password

    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    time.sleep(3)

    total_jobs = len(job_data)
    for job in job_data:
        job_title = job.get("job_position")
        job_link = job.get("job_link")
        job_company_name = job.get("company_name")
        job_location = job.get("job_location")
        job_posting_date = job.get("job_posting_date")
    
        if job_link:
            #try 5 times
            for attempt in range(1, 6):
                try:
                    driver.get(job_link)
                    time.sleep(random.uniform(2, 5))  # Randomize time to run more human like
                    
                    # Get the job description
                    job_desc = driver.find_element(By.CLASS_NAME, 'jobs-description__container')
                    soup = BeautifulSoup(job_desc.get_attribute('outerHTML'), 'html.parser')
                    job_description = soup.get_text(strip=True)

                    # Print the job description
                    if job_description:
                        print(f"Job description found for {job_title}.")
                    else:
                        print(f"No job description found for {job_title}.")
    
                    # Get the number of applicants
                    applicants_element = driver.find_element(By.XPATH, "//li[contains(@class, 'jobs-premium-applicant-insights__list-item') and contains(., 'Applicants in the past day')]//span[contains(@class, 'jobs-premium-applicant-insights__list-num')]")

                    number_of_applicants = applicants_element.text.strip()

                    # Print the number of applicants
                    if number_of_applicants:
                        print(f"Number of applicants found for {job_title}: {number_of_applicants}.")
                    else:
                        print(f"No applicants found for {job_title}.")

                    # Insight extraction : you can check with chrome developer tools to see if this is the correct xpath incase it changes
                    insight_xpath = "//li[contains(@class, 'job-details-jobs-unified-top-card__job-insight')]/span/span"
                    insight_container = None
                    
                    # Attempt to find insights
                    for insight_attempt in range(1, 6):
                        try:
                            insight_container = driver.find_elements(By.XPATH, insight_xpath)
                            break
                        except NoSuchElementException:
                            time.sleep(2 ** insight_attempt + random.uniform(1, 3))
                    
                    # Initialize values for  insights
                    contract_type, experience_level, flexibility = "N/A", "N/A", "N/A"
                    
                    if insight_container:
                        print(f"Extracting insights for {job_title}...")
                        span_texts = [span.text.strip() for span in insight_container if span.text.strip()]
                    
                        # Log the extracted span texts for debugging
                        print(f"Span texts found: {span_texts}")
                    
                        # Check for keywords in the collected span texts
                        for text in span_texts:
                            if any(keyword in text for keyword in ["Full-time", "Part-time", "Temporary", "Contract", "Internship"]):
                                contract_type = next((keyword for keyword in ["Full-time", "Part-time", "Temporary", "Contract", "Internship"] if keyword in text), "N/A")
                    
                            if any(keyword in text for keyword in ["Mid-Senior level", "Entry level", "Director", "Internship", "Executive", "Associate"]):
                                experience_level = next((keyword for keyword in ["Mid-Senior level", "Entry level", "Director", "Internship", "Executive", "Associate"] if keyword in text), "N/A")
                    
                            if any(keyword in text for keyword in ["Hybrid", "Remote", "On-site"]):
                                flexibility = next((keyword for keyword in ["Hybrid", "Remote", "On-site"] if keyword in text), "N/A")
                    
                        # Print insights found
                        print(f"Insights found for {job_title}: Contract Type - {contract_type}, Experience Level - {experience_level}, Flexibility - {flexibility}.")
                    else:
                        print(f"No insights found for {job_title}.")



                    # Append job data
                    job_descriptions.append({
                        "job_title": job_title,
                        "job_link": job_link,
                        "job_description": job_description,
                        "company_name": job_company_name,
                        "job_location": job_location,
                        "job_posting_date": job_posting_date,
                        "number_of_applicants": number_of_applicants,
                        "contract_type": contract_type,
                        "experience_level": experience_level,
                        "flexibility": flexibility
                    })
                    break  # Exit retry loop if successful
                except NoSuchElementException:
                    logging.info(f"Job description or applicants not found for {job_title}, attempt {attempt}")
                    time.sleep(2 ** attempt + random.uniform(1, 3))
                except Exception as e:
                    logging.error(f"Error loading the job link {job_link}: {e}")
                    break
    
finally:
    driver.quit()


# Combine original job data with all extra details
for job, description in zip(job_data, job_descriptions):
    job.update(description)  # This will keep all original data and add new fields

# Save combined job data to a new JSON file
with open('150_job_descriptions_data_analyst_last_day.json', 'w') as json_file:
    json.dump(job_data, json_file, indent=4)

# Convert JSON to CSV
csv_file = '150_job_descriptions_data_analyst_last_day.csv'

with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        "job_title", "job_link", "company_name", "job_location", "job_posting_date",
        "job_description", "number_of_applicants", "contract_type", "experience_level", "flexibility"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(job_descriptions)

# Print the number of successful job descriptions found and the total jobs processed
successful_jobs = len(job_descriptions)
print("Job descriptions and applicant counts saved to updated_job_descriptions_data_scientist.json")
print(f"Total jobs processed: {total_jobs}")
print(f"Total successful job descriptions found: {successful_jobs}")
print(f"CSV file saved as {csv_file}")
