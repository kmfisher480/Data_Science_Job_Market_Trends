import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from Appendix_1_Data_Scientist_Analyst_Job_Keywords import skill_areas_
import matplotlib.pyplot as plt

# Check if CSV files exist and load them conditionally
df_analyst = pd.read_csv('job_keywords_analyst_combined.csv') if os.path.exists('job_keywords_analyst_combined.csv') else None
df_scientist = pd.read_csv('job_keywords_scientist_combined.csv') if os.path.exists('job_keywords_scientist_combined.csv') else None

# Use multiple qualitative colors from Plotly
color_palette_plotly = px.colors.qualitative.Plotly

# Use a Matplotlib color palette (e.g., 'tab10' which has 10 unique colors)
color_palette_matplotlib = plt.get_cmap('tab10').colors

# Combine the color palettes
combined_palette = color_palette_plotly + list(color_palette_matplotlib)

# If you still need more colors, you can use a colormap with more colors
more_colors = plt.get_cmap('Set3', 12).colors  # 'Set3' has 12 distinct colors

# Combine palettes again if necessary
combined_palette.extend(more_colors)

# Create color map
color_map = {skill: combined_palette[i % len(combined_palette)] for i, skill in enumerate(skill_areas_)}

# Print the color mapping
print(color_map)



# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Jobs Keywords Dashboard"),

    # Dropdown to filter by skill area with "Select All" option
    dcc.Dropdown(
        id='skill-area-dropdown',
        options=[{'label': 'Select All', 'value': 'ALL'}] +
                [{'label': category, 'value': category} for category in (df_analyst['skill_area'].unique() if df_analyst is not None else [])],
        multi=True,
        value=(df_analyst['skill_area'].unique().tolist() if df_analyst is not None else []),
        placeholder="Select Skill Areas"
    ),
    
    # Slider to select the number of top skills to display on graphs
    dcc.Slider(
        id='top-skills-slider',
        min=1,
        max=20,  # Adjust based on your data
        value=5,  # Default value
        marks={i: str(i) for i in range(1, 21)},
        step=1,
        tooltip={"always_visible": True, "placement": "bottom"}
    ),

    # Button to export data
    html.Button("Export Data", id="export-button", n_clicks=0),

    # Text box to display total jobs analyzed
    html.Div(id='total-jobs-text', style={'fontSize': 18, 'marginBottom': 20}),
    # Text box to display total jobs analyzed
    html.Div(id='total-jobs-text-scientist', style={'fontSize': 18, 'marginBottom': 20}),

    # Graph for Data Analyst jobs (conditionally filled with data later)
    dcc.Graph(id='analyst-keywords-bar-chart'),
    
    # Graph for Data Scientist jobs (conditionally filled with data later)
    dcc.Graph(id='scientist-keywords-bar-chart'),

    dcc.Download(id='download-dataframe-csv')
])

# Callback to Update Analyst Bar Chart
@app.callback(
    [Output('analyst-keywords-bar-chart', 'figure'),
     Output('total-jobs-text', 'children')],
    [Input('skill-area-dropdown', 'value'),
     Input('top-skills-slider', 'value')]
)
def update_analyst_chart(selected_skills, top_x):
    if df_analyst is None:
        return {}, "No data available for Data Analyst jobs."

    df_analyst_filtered = df_analyst.copy()
    if selected_skills and 'ALL' not in selected_skills:
        df_analyst_filtered = df_analyst_filtered[df_analyst_filtered['skill_area'].isin(selected_skills)]

    unique_jobs_count_analyst = df_analyst_filtered['job_id'].nunique()
    melted_analyst = df_analyst_filtered.melt(id_vars=['job_id', 'job_title', 'company_name', 'job_location', 'skill_area'],
                                              value_vars=[col for col in df_analyst_filtered.columns if col not in ['job_id', 'job_title', 'company_name', 'job_location', 'skill_area']],
                                              var_name='Keyword', value_name='Presence')
    melted_analyst = melted_analyst[melted_analyst['Presence'] == 1]
    keyword_counts_analyst = melted_analyst['Keyword'].value_counts()
    top_keywords_analyst = keyword_counts_analyst.nlargest(top_x)

    # Prepare the DataFrame for plotting (sorted by Count in descending order)
    plot_df_analyst = (melted_analyst[melted_analyst['Keyword'].isin(top_keywords_analyst.index)]
                        .groupby(['Keyword', 'skill_area'])
                        .size()
                        .reset_index(name='Count')
                        .sort_values(by='Count', ascending=False))

    # Calculate the percentage of jobs for each keyword
    plot_df_analyst['Percentage'] = (plot_df_analyst['Count'] / unique_jobs_count_analyst) * 100
    print(plot_df_analyst.head())  # Check if the DataFrame has valid data
    print(plot_df_analyst.columns)  # Ensure all required columns are present
    print(color_map)  # Confirm the color map has all necessary mappings
    print(plot_df_analyst.head())
    print(plot_df_analyst.info())

    # Create the bar chart for Analyst
    fig_analyst = px.bar(plot_df_analyst,
                          x='Keyword',
                          y='Count',
                          title='Most Common Keywords for Data Analyst Jobs',
                          color='skill_area',
                          labels={'Keyword': 'Keywords', 'Count': 'Number of Jobs'},
                          text=plot_df_analyst['Count'].astype(str) + ' (' + plot_df_analyst['Percentage'].round(1).astype(str) + '% of jobs)',
                          color_discrete_map=color_map)

    fig_analyst.update_yaxes(range=[0, unique_jobs_count_analyst])
    total_jobs_text = f"Total jobs analyzed - Data Analyst: {unique_jobs_count_analyst}."
    
    return fig_analyst, total_jobs_text


# Callback to Update Scientist Bar Chart
@app.callback(
    [Output('scientist-keywords-bar-chart', 'figure'),
     Output('total-jobs-text-scientist', 'children')],
    [Input('skill-area-dropdown', 'value'),
     Input('top-skills-slider', 'value')]
)
def update_scientist_chart(selected_skills, top_x):
    if df_scientist is None:
        return {}

    df_scientist_filtered = df_scientist.copy()
    if selected_skills and 'ALL' not in selected_skills:
        df_scientist_filtered = df_scientist_filtered[df_scientist_filtered['skill_area'].isin(selected_skills)]

    unique_jobs_count_scientist = df_scientist_filtered['job_id'].nunique()
    melted_scientist = df_scientist_filtered.melt(id_vars=['job_id', 'job_title', 'company_name', 'job_location', 'skill_area'],
                                                  value_vars=[col for col in df_scientist_filtered.columns if col not in ['job_id', 'job_title', 'company_name', 'job_location', 'skill_area']],
                                                  var_name='Keyword', value_name='Presence')
    melted_scientist = melted_scientist[melted_scientist['Presence'] == 1]
    keyword_counts_scientist = melted_scientist['Keyword'].value_counts()
    top_keywords_scientist = keyword_counts_scientist.nlargest(top_x)

    # Prepare the DataFrame for plotting (sorted by Count in descending order)
    plot_df_scientist = (melted_scientist[melted_scientist['Keyword'].isin(top_keywords_scientist.index)]
                        .groupby(['Keyword', 'skill_area'])
                        .size()
                        .reset_index(name='Count')
                        .sort_values(by='Count', ascending=False))

    # Calculate the percentage of jobs for each keyword
    plot_df_scientist['Percentage'] = (plot_df_scientist['Count'] / unique_jobs_count_scientist) * 100

    # Create the bar chart for Scientist
    fig_scientist = px.bar(plot_df_scientist,
                          x='Keyword',
                          y='Count',
                          title='Most Common Keywords for Data Scientist Jobs',
                          color='skill_area',
                          labels={'Keyword': 'Keywords', 'Count': 'Number of Jobs'},
                          text=plot_df_scientist['Count'].astype(str) + ' (' + plot_df_scientist['Percentage'].round(1).astype(str) + '% of jobs)',
                          color_discrete_map=color_map)

    fig_scientist.update_yaxes(range=[0, unique_jobs_count_scientist])
    total_jobs_text_scientist = f"Total jobs analyzed - Data Scientist: {unique_jobs_count_scientist}."

    return fig_scientist, total_jobs_text_scientist


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
