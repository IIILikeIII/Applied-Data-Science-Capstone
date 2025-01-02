# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=[
                                    {'label': 'All Sites', 'value': 'ALL'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True

                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=1000,
                                marks={0: '0',2500: '2500',5000: '5000',7500: '7500'},
                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        pie_all = spacex_df.groupby('Launch Site')['class'].mean().reset_index()
        fig = px.pie(pie_all, values='class', 
        names='Launch Site', 
        title='Total Success Launches by Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        pie_site = filtered_df['class'].value_counts().reset_index()
        fig = px.pie(pie_site, values='count', 
        names='class', 
        title= f"Total Success Launches for site {entered_site}")    
        return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def success_payload_scatter_chart(entered_site, payload_slider):
    # Filter data based on payload range from slider
    payload_min, payload_max = payload_slider
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_min) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_max)]
    
    # Encode Booster Version Category
    filtered_df['Booster Version Numeric'] = filtered_df['Booster Version Category'].astype('category').cat.codes
    category_mapping = dict(enumerate(filtered_df['Booster Version Category'].astype('category').cat.categories))
    
    # Define a color palette for the categories
    colors = px.colors.qualitative.Vivid  # Use a predefined color palette
    color_map = {category: colors[i % len(colors)] for i, category in enumerate(category_mapping.values())}

    fig = go.Figure()

    if entered_site == 'ALL':
        # Create a scatter plot with separate traces for each category
        for category, color in color_map.items():
            category_df = filtered_df[filtered_df['Booster Version Category'] == category]
            fig.add_trace(go.Scatter(
                x=category_df['Payload Mass (kg)'],
                y=category_df['class'],
                mode='markers',
                marker=dict(color=color, size=10),
                name=category  # Add category name to legend
            ))
        # Update layout
        fig.update_layout(
            title='Payload and Launch Site by Booster Version Category',
            xaxis_title='Payload Mass (kg)',
            yaxis_title='Class',
            legend_title=dict(text='Booster Version Category'),
            xaxis=dict(range=[payload_min, payload_max])  # Set x-axis range based on slider
        )
    else:
        # Filter data for the selected launch site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        for category, color in color_map.items():
            category_df = site_df[site_df['Booster Version Category'] == category]
            fig.add_trace(go.Scatter(
                x=category_df['Payload Mass (kg)'],
                y=category_df['class'],
                mode='markers',
                marker=dict(color=color, size=10),
                name=category  # Add category name to legend
            ))
        # Update layout
        fig.update_layout(
            title=f'Payload at {entered_site} by Booster Version Category',
            xaxis_title='Payload Mass (kg)',
            yaxis_title='Class',
            legend_title=dict(text='Booster Version Category'),
            xaxis=dict(range=[payload_min, payload_max])  # Set x-axis range based on slider
        )
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
