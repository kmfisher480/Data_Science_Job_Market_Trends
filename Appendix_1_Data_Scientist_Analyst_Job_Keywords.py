# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 09:13:15 2024

@author: KatieFisher
"""

keywords_by_area = {
    "Programming Languages": {
        "keywords": {
            "Python": ["python"],
            "R": [" r "],
            "SQL": ["sql"],
            "Java": ["java"],
            "SAS": ["sas"],
            "JavaScript": ["javascript"],
            "MATLAB": ["matlab"],
            "C++": ["c++"],
            "Scala": ["scala"]
        }
    },
    "Data Analysis & Statistics": {
        "keywords": {
            "Machine Learning": [" ml ", "machine learning", "deep learning"],
            "Statistics": ["statistics", "statistical"],
            "Predict": ["predict", "predictive"],
            "Modeling": ["modeling", "modelling"],
            "Data Cleaning": ["data cleaning"],
            "Data Mining": ["data mining"],
            "Hypothesis or A/B Testing": ["hypothesis testing", "A/B"],
            "Bayesian Inference": ["bayesian inference"],
            "Linear or Logistic Regression": ["linear regression", "logistic regression", "regression"],
            "Logistic Regression": ["logistic regression"],
            "Random Forest": ["random forest"],
            "Support Vector Machines (SVM)": ["svm"],
            "Clustering": ["clustering"],
            "K-Means": ["k-means"],
            "ARIMA": ["arima"],
            "Time Series Analysis": ["time series analysis"],
            "Cross-validation": ["cross-validation"],
            "ROC/AUC": [" roc ", " auc "],
            "Confusion Matrix": ["confusion matrix"],
            "Neural Networks": ["neural network"]
        }
    },
    "Data Visualization & Dashboards": {
        "keywords": {
            "Tableau": ["tableau"],
            "Power BI": ["power bi"],
            "Matplotlib": ["matplotlib"],
            "Seaborn": ["seaborn"],
            "Looker": ["looker"],
            "Python Dashboards": ["python dashboards", "dash ", "plotly dash"],
            "Metabase": ["metabase"]
        }
    },
    "Big Data Technologies": {
        "keywords": {
            "Big Data": ["big data"],
            "Hadoop": ["hadoop"],
            "Apache Spark": ["apache spark"],
            "Kafka": ["kafka"],
            "AWS": ["aws"],
            "Azure": ["azure"],
            "Google Cloud Platform": ["google cloud platform"],
            "Snowflake": ["snowflake"],
            "Redshift": ["redshift"],
            "Google BigQuery": ["google bigquery"],
            "Microsoft SQL Server": ["microsoft sql server"]
        }
    },
    "Data Wrangling & ETL": {
        "keywords": {
            "Data Wrangling": ["data wrangling"],
            "ETL": ["etl", "elt"],
            "Apache NiFi": ["apache nifi"],
            "Talend": ["talend"]
        }
    },
    "Cloud Computing & Deployment": {
        "keywords": {
            "AWS Lambda": ["aws lambda"],
            "Docker": ["docker"],
            "Kubernetes": ["kubernetes"],
            "CI/CD": ["ci/cd"],
            "Jenkins": ["jenkins"],
            "CircleCI": ["circleci"]
        }
    },
    "Python Data Processing Libraries": {
        "keywords": {
            "Pandas": ["pandas"],
            "NumPy": ["numpy"],
            "TensorFlow": ["tensorflow"],
            "Keras": ["keras"],
            "PyTorch": ["pytorch"],
            "Scikit-learn": ["scikit-learn"],
            "Seaborn": ["seaborn"],
            "Matplotlib": ["matplotlib"],
            "Flask": ["flask"],
            "FastAPI": ["fastapi"],
            "BeautifulSoup": ["beautifulsoup"],
            "Scrapy": ["scrapy"],
            "Selenium": ["selenium"]
        }
    },
    "Natural Language Processing (NLP)": {
        "keywords": {
            "NLP": ["nlp", "natural language processing"],
            "spaCy": ["spacy"],
            "NLTK": ["nltk"]
        }
    },
    "Web Development": {
        "keywords": {
            "Flask": ["flask"],
            "FastAPI": ["fastapi"],
            "RESTful APIs": ["restful apis"],
            "Web Scraping": ["web scraping"],
            "BeautifulSoup": ["beautifulsoup"],
            "Scrapy": ["scrapy"],
            "Selenium": ["selenium"]
        }
    },
    "Version Control": {
        "keywords": {
            "Git": ["git"],
            "GitHub": ["github"],
            "GitLab": ["gitlab"]
        }
    },
    "Other Data Skills": {
        "keywords": {
            "Data Imputation": ["data imputation"],
            "Feature Engineering": ["feature engineering"],
            "Data Pipelines": ["data pipelines"],
            "Jupyter Notebooks": ["jupyter notebooks"]
        }
    },
    "Other Broader Skills": {
        "keywords": {
            "Communication": ["communication"],
            "Technical Communication": ["technical communication"],
            "Team Work": ["Team Work"],
            "Project Management": ["project management"],
            "Stakeholder Management": ["stakeholder management", "stakeholder engagement", "stakeholder collaboration"],
            "People Management": ["People Management", "Team Management"]
        }
    }
}

# Additional keywords
keywords_by_area_additional = {
    "Company Reputation & Industry": {
        "keywords": {
            "Tech Company": ['growth stage', "innovative", "cutting-edge", "tech company", "fintech", "startup culture", 'unicorn', 'global company'],
            "Financial Institution": ["bank", "financial institution", "regulated environment", "compliance"],
            "Growth-Oriented": ["high-growth", "rapidly expanding", "growth-oriented", 'fast-paced', 'ambiguity', 'curiosity'],
            "Reputation": ["leading", "award-winning", "industry leader"],
            "Work-Life Balance": ["work-life balance", "flexible working", 'hybrid'],
            "Sustainability": ["sustainability", "environmentally conscious"],
            "Benefits": ["health spending account", "bonus"],
            "Diversity & Inclusion": ["diversity", "inclusion", "equal opportunity", "inclusive culture"]
        }
    }
}

# Function to combine both dictionaries
def combine_keywords(original, additional):
    combined = original.copy()  # Start with a copy of the original
    for area, keywords in additional.items():
        if area in combined:
            combined[area]["keywords"].update(keywords["keywords"])  # Merge keywords if area exists
        else:
            combined[area] = keywords  # Add new area if it doesn't exist
    return combined


# Generating original_columns
keywords_no_synonyms = [
    keyword for area in keywords_by_area.values()
    for keyword in area["keywords"].keys()
]

# Combine the keywords
keywords_by_area_with_company_related_keywords = combine_keywords(keywords_by_area, keywords_by_area_additional)

# Generating original_columns
keywords_no_synonyms_additional = [
    keyword for area in keywords_by_area_with_company_related_keywords.values()
    for keyword in area["keywords"].keys()
]

# New structure to hold only main titles and their keywords without synonyms
skill_subgroups = {}

# Iterate through the original dictionary to build the new one
for area, data in keywords_by_area.items():
    # Extract the keywords without synonyms
    keywords = list(data["keywords"].keys())  # Get the main keywords
    skill_subgroups[area] = keywords  # Assign to new dictionary

# Display the new structure
#print(skill_subgroups)

# New structure to hold only main titles qith company words and their keywords without synonyms
skill_subgroups_with_company_words = {}

# Iterate through the original dictionary to build the new one
for area, data in keywords_by_area_with_company_related_keywords.items():
    # Extract the keywords without synonyms
    keywords = list(data["keywords"].keys())  # Get the main keywords
    skill_subgroups_with_company_words[area] = keywords  # Assign to new dictionary

# Display the new structure
#print(skill_subgroups_with_company_words)


subgroups_company_words = {}

# Iterate through the original dictionary to build the new one
for area, data in keywords_by_area_additional.items():
    # Extract the keywords without synonyms
    keywords = list(data["keywords"].keys())  # Get the main keywords
    subgroups_company_words[area] = keywords  # Assign to new dictionary

# Display the new structure
#print(subgroups_company_words)

skill_areas_ = list(keywords_by_area.keys())
