import json
import pandas as pd
import re
from transformers import pipeline
import seaborn as sns
import matplotlib.pyplot as plt
from Appendix_1_Data_Scientist_Analyst_Job_Keywords import keywords_by_area_with_company_related_keywords, keywords_no_synonyms, keywords_by_area

#NOTE: replace 'xxxxx' with your own info!

with open(r'C:\Users\KatieFisher\OneDrive - Manna\Documents\0 - Learning\1 - Python\ForGithub\Resume_Matcher_and_Top_Skills_For_Data_Scientists_and_Analysts\150_job_descriptions_data_analyst_last_day.json', 'r') as json_file: #add file path for file location
    job_data = json.load(json_file)


# Initialize the sentiment analysis pipeline using a specific fine-tuned BERT model. Not used just interesting
sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Initialize a list to store job data with keywords
job_list = []

#function to extract salary values. Only suitable for CAD. Would need to be updated
def extract_salary_values(text):
    # Define patterns for values with and without 'k' (i.e $100k)
    #takes currence symbols as $, C, CAD, or any combination of these
    pattern_simple_k = r"([$CADC]?)\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?\s*k\b"  # Simple amounts with 'k'
    pattern_range_k = r"([$CADC]?)\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?\s*k\s*(?:[-–]|\bto\b)\s*([$CADC]?)\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?\s*k\b"  # Range with 'k'
    pattern_simple = r"([$CADC]?)\s*(\d{1,7}(?:,\d{3})*|\d+)(?:\.\d+)?\b"  # Simple amounts without 'k'
    pattern_range = r"([$CADC]?)\s*(\d{1,7}(?:,\d{3})*|\d+)(?:\.\d+)?\s*[-–]\s*([CAD\$]? ?(?:C|A|D)? ?(?:\$)?)\s*(\d{1,7}(?:,\d{3})*|\d+)(?:\.\d+)?"  #Range without 'k'
   
    # Perform regex matching
    matches_range_k = re.findall(pattern_range_k, text)  # Range with 'k'
    matches_simple_k = re.findall(pattern_simple_k, text) # Simple with 'k'
    matches_range = re.findall(pattern_range, text)        # Range without 'k'
    matches_simple = re.findall(pattern_simple, text)      # Simple without 'k'

    # Function to filter matches to include only those with at least one currency symbol
    def filter_currency(matches):
        return [match for match in matches if any(symbol in match for symbol in ('$','C','A','D'))]

    # Filter range matches with and without 'k' and add 'k' to the end
    filtered_range_k = filter_currency(matches_range_k)
    filtered_range_k = [match + ('k',) for match in filtered_range_k]  # Adding 'k'

    filtered_range = filter_currency(matches_range)

    # Filter simple matches with and without 'k' and add 'k' to the end
    filtered_simple_k = filter_currency(matches_simple_k)
    filtered_simple_k = [match + ('k',) for match in filtered_simple_k]  # Adding 'k'

    filtered_simple = filter_currency(matches_simple)

    # If any range match exists (prioritize range matches)
    if filtered_range_k:
        final_matches = filtered_range_k
    elif filtered_range:
        final_matches = filtered_range
    else:
        # If no range match, use simple matches
        final_matches = filtered_simple_k + filtered_simple

    # Only keep final matches that have at least one currency symbol
    final_matches = filter_currency(final_matches)

    # Initialize lower and upper salary
    lower_salary = None
    upper_salary = None
    
    # Process the matches to extract salary values
    if final_matches:
        # Check for range matches
        if len(final_matches[0]) >= 4:  # For range matches
            low = float(final_matches[0][1].replace(',', '').strip()) if final_matches[0][1].strip() else 0.0
            high = float(final_matches[0][3].replace(',', '').strip()) if final_matches[0][3].strip() else 0.0
            
            # Check for 'k' in the last element of the match
            if final_matches[0][-1] == 'k':  # If 'k' is present in the last element
                low *= 1000
                high *= 1000
            
            lower_salary = low
            upper_salary = high
            
            if lower_salary < 30000:
                lower_salary = None

            if upper_salary < 30000:
                upper_salary = None

        
        # Check for single matches
        elif len(final_matches[0]) >= 2 and final_matches[0][1].strip():
            num = float(final_matches[0][1].replace(',', '').strip()) if final_matches[0][1].strip() else 0.0
            
            # Check for 'k' in the last element of the match
            if final_matches[0][-1] == 'k':  # If 'k' is present in the last element
                num *= 1000  # Multiply by 1000 if 'k' is present
            
            lower_salary = num
            upper_salary = None  # No upper salary for single amounts
            if lower_salary < 30000:
                lower_salary = None

    return lower_salary, upper_salary


# Loop through job descriptions to check for salary and complete sentiment analysis
for job in job_data:
    job_entry = {key: job.get(key, "") for key in job.keys()}  # Get all job data as is
    job_description = job_entry.get("job_description", "").lower()  # Convert to lowercase for matching

    # Extract salary
    lower_salary, upper_salary = extract_salary_values(job_description)

    # Add extracted salary to job 
    job_entry['lower_salary'] = lower_salary
    job_entry['upper_salary'] = upper_salary
    
    
    # Sentiment Analysis using BERT
    if job_description:  # Check if the job description is not empty
        max_length = 512
        truncated_description = job_description[:max_length]  # Truncate to max length
        analysis = sentiment_pipeline(truncated_description)
        sentiment_label = analysis[0]['label']
        sentiment_score = analysis[0]['score'] if sentiment_label == 'POSITIVE' else -analysis[0]['score']
    else:
        sentiment_score = None
        sentiment_label = None


    # Add sentiment to job entry
    job_entry['sentiment_score'] = sentiment_score
    job_entry['sentiment_label'] = sentiment_label

    # Check for each category of keywords in the job description
    for category, category_info in keywords_by_area_with_company_related_keywords.items():
        keyword_dict = category_info['keywords']
        
        # Create a set to track counted keywords
        counted_keywords = set()
        
        for keyword, synonyms in keyword_dict.items():
            # Check if any synonym is in the job description
            if any(synonym in job_description for synonym in synonyms):  # Match case-insensitive
                counted_keywords.add(keyword)

        # Assign 1 if any synonym is found, otherwise 0
        for keyword in counted_keywords:
            job_entry[keyword] = 1
        # If no keywords from this category were found, set them to 0
        for keyword in keyword_dict.keys():
            if keyword not in counted_keywords:
                job_entry[keyword] = 0


    job_list.append(job_entry)


df = pd.DataFrame(job_list)

# Convert columns to numeric, forcing errors to NaN
df['number_of_applicants'] = pd.to_numeric(df['number_of_applicants'], errors='coerce')
df['number_of_applicants'] = df['number_of_applicants'].fillna(0)
df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')

# Drop rows with missing values in either column
df_clean = df.dropna(subset=['number_of_applicants', 'sentiment_score'])

# Save the cleaned DataFrame to a CSV file, if needed
df_clean.to_csv('job_keywords_analyst_cleaned_today.csv', index=False)

#regression plot for number of applicants vs. sentiment score
plt.figure(figsize=(10, 6))
sns.regplot(x='number_of_applicants', y='sentiment_score', data=df_clean, scatter_kws={'alpha':0.5})
plt.title('Regression Plot: Number of Applicants vs Sentiment Score')
plt.xlabel('Number of Applicants')
plt.ylabel('Sentiment Score')
plt.grid(True)
plt.show()

print(df_clean[['lower_salary', 'upper_salary']].head(50))
print(df_clean[['lower_salary', 'upper_salary']].tail(50))

print(df_clean[['lower_salary', 'upper_salary']].isnull().sum())
print(df_clean[['lower_salary', 'upper_salary']].notnull().sum())


# Plotting histogrm of number of applicants
plt.figure(figsize=(10, 6))
plt.hist(df_clean['number_of_applicants'], bins=20)  # Adjust bins as necessary
plt.xlabel('Number of Applicants')
plt.ylabel('Frequency')
plt.title('Distribution of Number of Applicants')
plt.show()


# Create separate DataFrames for each skill area
dataframes_by_category = {}

for category, category_info in keywords_by_area.items():
    keyword_dict = category_info['keywords']
    
    # Filter only the columns related to this category
    category_df = df[['job_id', 'job_title', 'company_name', 'job_location'] + list(keyword_dict.keys())]  # Include Job ID
    
    # Add a column for the skill area using .loc to avoid SettingWithCopyWarning
    category_df.loc[:, 'skill_area'] = category  
    
    # Reorder columns to have 'Skill Area' before the keywords
    category_df = category_df[['job_id', 'job_title', 'company_name', 'job_location', 'skill_area'] + list(keyword_dict.keys())]  # Include Job ID

    dataframes_by_category[category] = category_df

# Combine all category DataFrames into a single DataFrame
combined_df = pd.concat(dataframes_by_category.values(), ignore_index=True)

# Output the combined DataFrame
print(combined_df)

# Save the combined DataFrame to a CSV file (optional)
combined_df.to_csv('job_keywords_analyst_combined.csv', index=False)
