import pandas as pd
import panel as pn
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
import numpy as np

pn.extension(sizing_mode="stretch_width")

df = pd.read_csv('../StudentPerformanceFactors.csv')
def score_group(score):
    if 55 <= score < 60:
        return '55-59'
    elif 60 <= score < 65:
        return '60-64'
    elif 65 <= score < 70:
        return '65-69'
    elif 70 <= score < 75:
        return '70-74'
    elif 75 <= score < 80:
        return '75-79'
    elif 80 <= score < 85:
        return '80-84'
    elif 85 <= score < 90:
        return '85-89'
    elif 90 <= score <= 100:
        return '90-100'
    else:
        return 'Unknown'

df['Score Group'] = df['Exam_Score'].apply(score_group)
df['Exam_Score'] = pd.to_numeric(df['Exam_Score'], errors='coerce')
df = df.dropna(subset=['Exam_Score', 'Gender'])

def create_bar_chart(column, title):
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, 'Count']
    fig = px.bar(counts, x=column, y='Count', title=title, color=column)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20),
                      showlegend=False,
                      xaxis_title=column.replace("_", " "))
    return fig

gender_bar = create_bar_chart('Gender', 'Gender Distribution')
parental_bar = create_bar_chart('Parental_Involvement', 'Parental Involvement')
school_bar = create_bar_chart('School_Type', 'School Type Distribution')

density_fig = go.Figure()
colors = {'Male': '#1f77b4', 'Female': '#e377c2'}

for gender in df['Gender'].unique():
    scores = df[df['Gender'] == gender]['Exam_Score'].dropna()
    if len(scores) > 1:
        kde = gaussian_kde(scores)
        x_range = np.linspace(scores.min(), scores.max(), 200)
        y_vals = kde(x_range)
        density_fig.add_trace(go.Scatter(
            x=x_range,
            y=y_vals,
            mode='lines',
            name=gender,
            line=dict(color=colors[gender]),
            fill='tozeroy',
            opacity=0.5
        ))

density_fig.update_layout(
    title='Exam Score Distribution by Gender',
    xaxis_title='Exam Score',
    yaxis_title='Density',
    margin=dict(t=50, l=50, r=30, b=40)
)

sunburst_fig = px.sunburst(
    df,
    path=['Motivation_Level', 'Score Group'],
    title='Sunburst: Motivation Level → Exam Score',
    color='Motivation_Level',
    color_discrete_map={'Low': '#FF9999', 'Medium': '#FFCC99', 'High': '#99CCFF'}
)
sunburst_fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))

def styled_panel(plot, width, height):
    return pn.Column(
        pn.pane.Plotly(plot, width=width, height=height, sizing_mode="fixed"),
        styles={
            "background": "#f5f5f5",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "8px",
            "boxShadow": "1px 1px 5px rgba(0,0,0,0.04)",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center"
        },
        margin=(5, 5),
        width=width + 20
    )

row_widths = [310, 310, 310]
row_heights = 300

upper_row = pn.Row(
    styled_panel(gender_bar, width=row_widths[0], height=row_heights),
    styled_panel(parental_bar, width=row_widths[1], height=row_heights),
    styled_panel(school_bar, width=row_widths[2], height=row_heights),
    sizing_mode="fixed"
)

second_row = pn.Row(
    styled_panel(sunburst_fig, width=465, height=row_heights),
    styled_panel(density_fig, width=465, height=row_heights),
    sizing_mode="fixed"
)

layout = pn.Column(
    upper_row,
    second_row,
    sizing_mode="fixed",
    margin=(0, 10),
    width=930
)

layout.save("dashboard_demographic00.html", embed=True)
