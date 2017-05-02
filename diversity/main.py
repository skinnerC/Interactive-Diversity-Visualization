from os.path import dirname, join

from bokeh.layouts import layout, widgetbox
from bokeh.models import HoverTool, Div
from bokeh.models.widgets import Select, RadioButtonGroup
from bokeh.io import curdoc
from bokeh.charts import Donut, Bar, color
from bokeh.charts.attributes import CatAttr
from bokeh.palettes import Reds
from bokeh.models.ranges import Range1d

import pandas as pd

# Use the current company and year values to get appropiate data 
def select_data():
    company_val = company.value
    year_val = int(year.labels[year.active])

    gender_df = gender_data[(gender_data['Company'] == company_val) & 
                     (gender_data['Year'] == year_val)]
    race_df = race_data[(race_data['Company'] == company_val) & 
                     (race_data['Year'] == year_val)]
    
    return (gender_df, race_df)

# Updates charts
def update():
    global gender_df, race_df, l
    
    # Get new data
    gender_df, race_df = select_data()
    
    # Set page title
    curdoc().title = '{0} {1}'.format(gender_df['Company'].values[0],
                    int(gender_df['Year'].values[0]))
    
    # Make HoverTools
    tool = HoverTool()
    tool.tooltips = [('Race', '@Label'),
                     ('% of Workforce', '@height%'),]
    tool.show_arrow = False
    tool = [tool]
    
    tool2 = HoverTool()
    tool2.tooltips = [('Gender', '@Label'),
                     ('% of Workforce', '@values%'),]
    tool2.show_arrow = False
    tool2 = [tool2]
    
    # Create new race chart
    race = Bar(race_df, label=CatAttr(columns=['Label'], sort=False),
               values='Value', toolbar_location=None,
               background_fill_color='#caebf2', border_fill_alpha = 0,
               outline_line_alpha=0, ylabel='% of Workforce', xlabel='Race',
               plot_width=400, plot_height=400, legend='top_right',
               tools = tool, color=color(columns=['Label'], palette=Reds[5]))
    race.y_range=Range1d(0, 100)
    
    # Create new gender chart
    gender = Donut(gender_df, label='Label', values='Value',
                   toolbar_location=None, background_fill_color='#caebf2',
                   border_fill_alpha = 0, outline_line_alpha=0, width=370,
                   height=400, tools=tool2, hover_tool=False,
                   palette=['#a50f15','#fee5d9'])
    
    # Update the charts in the layout
    l.children[1].children = [race, gender]

# Create dataframes for race and gender data
race_data = pd.DataFrame(columns=['Company', 'Year', 'Label', 'Value'])
gender_data = pd.DataFrame(columns=['Company', 'Year', 'Label', 'Value'])

# Parse data.csv into dataframes
with open(join(dirname(__file__), 'data.csv'), 'r') as file:
    labels = file.readline().strip().split(',')
    
    for line in file:
        data = line.strip().split(',')
        
        # Parse gender data
        for i in range(2):
            gender_data = gender_data.append({
                    'Company': data[0],
                    'Year': int(data[1]),
                    'Label': labels[2+i],
                    'Value': int(data[2+i])
                    }, ignore_index=True)
        
        # Parse race data
        for i in range(len(labels) - 4):
            race_data = race_data.append({
                    'Company': data[0],
                    'Year': int(data[1]),
                    'Label': labels[4+i],
                    'Value': int(data[4+i]),
                    'Value_String': data[4+i]
                    }, ignore_index=True)

# Generate list of company names
names = gender_data['Company'].drop_duplicates()

# Load description.html
desc = Div(text=open(join(dirname(__file__),'description.html')).read(),
           width=800)

# Create controls
company = Select(options=list(names), value='US Population')
year = RadioButtonGroup(labels=['2014', '2015', '2016'], active=0)

company.on_change('value', lambda attr, old, new: curdoc().add_next_tick_callback(update))
year.on_change('active', lambda attr, old, new: curdoc().add_next_tick_callback(update))

controls = [company, year]

# Create dummy plots to establish layout
gender_df = gender_data[(gender_data['Company'] == 'Intel') & 
                     (gender_data['Year'] == 2014)]
race_df = race_data[(race_data['Company'] == 'Intel') & 
                     (race_data['Year'] == 2014)]

p = Donut(race_df, label='Label', values='Value')
q = Donut(gender_df, label='Label', values='Value')

# Create layout
sizing_mode = 'fixed'

inputs = [widgetbox(input, sizing_mode=sizing_mode, width=400) for input in controls]
l = layout([
        [desc],
        [p, q],
        [*inputs]
        ], sizing_mode=sizing_mode)

update()

# Add the layout to the page
curdoc().add_root(l)