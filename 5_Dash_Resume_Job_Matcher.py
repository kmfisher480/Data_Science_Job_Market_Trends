import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import PyPDF2
import base64
import tempfile
from Appendix_1_Data_Scientist_Analyst_Job_Keywords import keywords_by_area, keywords_no_synonyms #created keywords dictionary for single source of truth


# create an dash which allows user to upload resume (pdf) and see which jobs they are best matched to.
# Load your job skills data
job_data = pd.read_csv('job_keywords_scientist_cleaned_today.csv')

# Filter jobs based on the specified criteria (case-insensitive for job title matching)
job_data = job_data[
    (
        (job_data['job_title'].str.contains('Data Scientist', case=False) | 
         job_data['job_title'].str.contains('Data Analyst', case=False)) 
        | 
        (job_data.iloc[:, 18:].sum(axis=1) > 5)  # Count of skills greater than 5
    ) 
    & 
    (job_data['job_location'].str.contains('Canada', case=False))  # Job location contains 'Canada'
]


skills_data = job_data[keywords_no_synonyms]
skill_counts = skills_data.sum().sort_values(ascending=False)
top_skills = skill_counts.head(10).index.tolist()

def extract_text_from_pdf(contents):
    """Extract text from the uploaded PDF file."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp_pdf:
        temp_pdf.write(decoded)
        temp_pdf.seek(0)
        text = ""
        
        reader = PyPDF2.PdfReader(temp_pdf)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                print(f"No text found on page {page_num + 1} of the uploaded PDF")
                
    return text.strip()


def extract_skills_from_text(text):
    found_skills = []
    for area, data in keywords_by_area.items():
        for skill, synonyms in data['keywords'].items():
            for synonym in synonyms:
                if synonym.lower() in text.lower():
                    found_skills.append(skill)
                    break
    return found_skills

# function to match resume skills to job skills - what jobs does the resume cover the highest % of skills?
def extract_skills_and_match(contents):
    if contents is not None:
        resume_text = extract_text_from_pdf(contents)
        resume_skills = extract_skills_from_text(resume_text)
        
        if not isinstance(resume_skills, list) or len(resume_skills) == 0:
            return pd.DataFrame(), "No matching jobs found."

        resume_skills_normalized = [skill.lower().strip() for skill in resume_skills]

        best_matches = []

        for index, job in job_data.iterrows():
            job_title = job['job_title']
            company = job['company_name']
            location = job['job_location']
            posting_date = job['job_posting_date']
            job_link = job['job_link']
            
            # Get the required job skills from the job posting
            job_skills_required = job.iloc[18:]  # Get all skills starts at column 29 
            job_skills_required = job_skills_required[job_skills_required == 1].index.tolist()  # Filter to get skill names with value 1 (true)
            job_skills_required = [skill.lower().strip() for skill in job_skills_required]  # Normalize skill names

            # Compare resume skills with job skills
            match_count = sum([1 for skill in job_skills_required if skill in resume_skills_normalized])
            total_job_skills = len(job_skills_required)

            if total_job_skills > 0:
                match_percentage = (match_count / total_job_skills) * 100
            else:
                match_percentage = 0.0

            if match_percentage > 0:
                matching_skills = [skill for skill in job_skills_required if skill in resume_skills_normalized]
                best_matches.append({
                    'Job Posting Title': job_title,
                    'Company': company,
                    'Location': location,
                    'Posting Date': posting_date,
                    'Matching Skills': ", ".join(matching_skills),
                    'Match Percentage': match_percentage,  # Store as a float for easy sorting
                    'URL': job_link
                })

        # Sort the best matches by match percentage in descending order
        best_matches = sorted(best_matches, key=lambda x: x['Match Percentage'], reverse=True)

        #Take the top 10 matches
        top_matches = best_matches[:10]

        if top_matches:
            # Convert to DataFrame
            return pd.DataFrame(top_matches), f"Total Skills Found in Resume: {len(resume_skills)}"
        else:
            return pd.DataFrame(), "No matching jobs found."
    
    return pd.DataFrame(), "Upload a resume to see skills"



app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Resume to Job Matcher"),
    dcc.Upload(
        id='upload-resume',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a Resume')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-message'),
    dash_table.DataTable(id='matching-jobs-table')
])

@app.callback(
    [Output('matching-jobs-table', 'data'),
     Output('matching-jobs-table', 'columns'),
     Output('output-message', 'children')],
    [Input('upload-resume', 'contents')]
)

def update_output(contents):
    if contents is not None:
        matching_jobs, message = extract_skills_and_match(contents)

        if not matching_jobs.empty:
            columns = [{"name": i, "id": i} for i in matching_jobs.columns]
            data = matching_jobs.to_dict('records')
        else:
            columns = []
            data = []

        return data, columns, message
    
    return [], [], "Upload a resume to see matched jobs"

if __name__ == '__main__':
    app.run_server(debug=True)