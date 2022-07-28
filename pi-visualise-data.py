import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

# create a connection to the pi-traffic-lights sqlite3 Database
conn = sqlite3.connect('pi-traffic-lights.db')

# create a sidebar date selector
date = st.sidebar.date_input("Button Pressed Date")

# Get the earliest and latest date available in the data set
earliestDate = pd.read_sql("SELECT MIN(pressed_on)
                as EarliestDate from button_pressed", con=conn)
latestDate = pd.read_sql("SELECT MAX(pressed_on)
                  as LatestDate from button_pressed", con=conn)
st.write("Chart from ", 
         earliestDate.EarliestDate[0], "to ", 
         latestDate.LatestDate[0])

# Create a SQLite3 query for the whole stream of data
allDataQuery = "SELECT * from button_pressed"

# Create a Pandas DataFrame (df) based on the allDateQuery
df = pd.read_sql(allDataQuery, con=conn)

# Create a Chart that combines the USA/Beep values into a stacked bar chart
c = alt.Chart(df).transform_fold( # fold USA/Beep into "value" column
     ['usa', 'beep'],
     as_=['column', 'value']
    ).mark_bar().encode(
     # X Axis is based on the time parameter based on the day of the month
     x=alt.X('pressed_on:T', timeUnit='date'),
     # Y Axis uses the combined usa/beep "value" as a Quantatative parameter
     y='value:Q',
     color='column:N')

# Display the chart data using the altair_chart function from within streamlit
st.altair_chart(c)

# Create a SQLite3 query for all the data for a specific day
dateBasedQuery = "SELECT * from button_pressed
                  where pressed_on LIKE
                  '" + date.strftime("%Y-%m-%d%") + "'"

# Create a 2nd Pandas DataFrame for the selected date only
dateBasedData = pd.read_sql(dateBasedQuery, con=conn)

st.write("DataFrame for ", date.strftime("%Y-%m-%d"))
st.write(dateBasedData)

# close off the connection to sqlite3
conn.close()
