import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html

# Read the data
df = pd.read_csv('plot.csv')

# Calculate total disbursement per year for the static line graph
total_disbursement_per_year = df.groupby('Year')['Disbursed Amount (US$)'].sum().reset_index()

# Initialize the Dash app
app = Dash(__name__)
server = app.server

# Create the main figure
fig = go.Figure()

# Loop through each year to create frames for animation
years = sorted(df['Year'].unique())
for year in years:
    df_year = df[df['Year'] == year]
    
    # Add choropleth map for deviation
    fig.add_trace(go.Choropleth(
        locations=df_year['Country'],
        locationmode='country names',
        z=df_year['deviation_from_avg'],
        colorscale='RdYlBu',
        zmin=-df['deviation_from_avg'].abs().max(),
        zmax=df['deviation_from_avg'].abs().max(),
        colorbar=dict(
            title=dict(text='<br>Deviation from Mean<br>(+ve = Above Mean, -ve = Below Mean)', side='right'),
            tickvals=[-df['deviation_from_avg'].abs().max(), 0, df['deviation_from_avg'].abs().max()],
            ticktext=['Below Mean', 'At Mean', 'Above Mean']
        ),
        visible=(year == years[0])
    ))

    # Add spikes/protrusions for disbursed amounts
    fig.add_trace(go.Scattergeo(
        locations=df_year['Country'],
        locationmode='country names',
        text=df_year.apply(lambda row: f"{row['Country']}: ${row['Disbursed Amount (US$)']:.2e}", axis=1),
        marker=dict(
            size=df_year['Disbursed Amount (US$)'] / df['Disbursed Amount (US$)'].max() * 30,
            color='yellow',
            line=dict(width=1, color='darkorange')
        ),
        name='Disbursed Amount',
        mode='markers',
        visible=(year == years[0])
    ))

# Create frames for each year
frames = []
for year in years:
    frame_data = []
    df_year = df[df['Year'] == year]
    
    frame_data.append(go.Choropleth(
        locations=df_year['Country'],
        locationmode='country names',
        z=df_year['deviation_from_avg'],
        colorscale='RdYlBu',
        zmin=-df['deviation_from_avg'].abs().max(),
        zmax=df['deviation_from_avg'].abs().max(),
        colorbar=dict(
            title=dict(text='<br>Deviation from Mean<br>(+ve = Above Mean, -ve = Below Mean)', side='right'),
            tickvals=[-df['deviation_from_avg'].abs().max(), 0, df['deviation_from_avg'].abs().max()],
            ticktext=['Below Mean', 'At Mean', 'Above Mean']
        )
    ))

    frame_data.append(go.Scattergeo(
        locations=df_year['Country'],
        locationmode='country names',
        text=df_year.apply(lambda row: f"{row['Country']}: ${row['Disbursed Amount (US$)']:.2e}", axis=1),
        marker=dict(
            size=df_year['Disbursed Amount (US$)'] / df['Disbursed Amount (US$)'].max() * 30,
            color='purple',
            line=dict(width=1, color='darkorange')
        ),
        name='Disbursed Amount',
        mode='markers'
    ))

    frames.append(go.Frame(data=frame_data, name=str(year)))

# Create sliders and animation settings
steps = []
for i, year in enumerate(years):
    step = dict(
        method='animate',
        args=[[str(year)], dict(mode='immediate', frame=dict(duration=500, redraw=True), transition=dict(duration=300))],
        label=str(year),
        visible=True  # Make numerical labels visible
    )
    steps.append(step)

sliders = [dict(
    active=0,
    steps=steps,
    transition=dict(duration=300),
    len=0.9,
    x=0.1,
    y=0,
    tickcolor='rgba(0,0,0,0)',
    font=dict(color='rgba(0,0,0,0)')  # Make numerical labels visible
)]

# Update layout with sliders and automatic animation
fig.update_layout(
    title=dict(
        text='',
        x=0.5,
        y=0.95,
        font=dict(size=24, color='white', family='Arial'),
        xanchor='center'
    ),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="Black",
        projection_type='natural earth',
        landcolor='rgb(55, 55, 55)',
        oceancolor='rgb(35, 35, 35)',
        bgcolor='rgb(255, 228, 225)'  # Peach background color
    ),
    sliders=sliders,
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        buttons=[
            dict(label="Play",
                 method="animate",
                 args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True, mode='immediate')]),
            dict(label="Pause",
                 method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate')])
        ]
    )],
    margin=dict(l=0, r=0, t=50, b=0),
    legend=dict(title=dict(text='Legend', font=dict(size=16, color='white', family='Arial')), font=dict(color='white', family='Arial'))
)

fig.frames = frames

# Create a static line graph for total disbursement per year
line_fig = go.Figure()
line_fig.add_trace(go.Scatter(
    x=total_disbursement_per_year['Year'],
    y=total_disbursement_per_year['Disbursed Amount (US$)'],
    mode='lines+markers',
    line=dict(color='orange'),
    marker=dict(color='darkorange'),
    name='Total Disbursement'
))

line_fig.update_layout(
    title='Total Disbursement Amount per Year',
    xaxis_title='Year',
    yaxis_title='US$',
    plot_bgcolor='rgb(10, 10, 55)',  # Dark blue background color
    paper_bgcolor='rgb(10, 10, 55)',  # Dark blue background color
    font=dict(color='white', family='Arial'),
    margin=dict(l=40, r=40, t=50, b=50)
)

# Define layout for the Dash app
app.layout = html.Div([
    html.H1('Global Loan Disbursement and Creditworthiness Insights', style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '36px', 'fontWeight': 'bold', 'marginBottom': '20px'}),
    html.H2('A Comprehensive Analysis of IDA Loan Disbursements Over Time', style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '24px', 'marginBottom': '20px'}),
    html.P('Delve into the intricate dynamics of loan disbursements by the International Development Association (IDA) with this interactive dashboard. '
           'Our visualizations provide a dual perspective: the purple bubbles represent the actual amounts disbursed to each country per year, while the choropleth map highlights '
           'deviations from the average creditworthiness. By comparing the ratio of loan amounts demanded versus disbursed and analyzing deviations from yearly means, we uncover patterns of '
           'financial trustworthiness and funding efficiency across nations. Explore the trends and outliers that define the global landscape of loan disbursement.', 
           style={'textAlign': 'center', 'fontFamily': 'Arial', 'fontSize': '16px', 'color': 'white', 'margin': '0 auto', 'maxWidth': '800px'}),
    html.Div(style={'height': '2vh'}),  # Spacer
    html.Div([
        dcc.Graph(id='map-animation', figure=fig, style={'height': '75vh', 'width': '100%'}),
        dcc.Graph(id='line-graph', figure=line_fig, style={'height': '35vh', 'width': '100%'}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
    html.Div(style={'height': '2vh'})  # Spacer
], style={'backgroundColor': 'rgb(173, 216, 230)', 'color': 'white', 'padding': '20px'})  # Light blue background color

if __name__ == '__main__':
    app.run_server(debug=True)
