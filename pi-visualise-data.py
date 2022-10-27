import sqlite3 
import pandas as pd
import streamlit as st
import altair as alt

# create a connection to the pi-traffic-lights.db sqlite3 Database
conn = sqlite3.connect('pi-traffic-lights.db')

# create a sidebar date selector
date = st.sidebar.date_input("Button Pressed Date")

# get the earliest and latest dates in the data set
earliestDate = pd.read_sql(
    "SELECT MIN(pressed_on) as EarliestDate from button_pressed",
    con=conn)
latestDate = pd.read_sql(
    "SELECT MAX(pressed_on) as LatestDate from button_pressed",
    con=conn)
st.write("Chart from ",
    earliestDate.EarliestDate[0], " to ",
    latestDate.LatestDate[0])

# Create a Pandas DataFrame (df) by reading the button_pressed table
df = pd.read_sql("SELECT * from button_pressed", con=conn)

# Create a Chart that combines the USA/Beep values into a stacked bar chart
c = alt.Chart(df).transform_fold( # fold USA/Beep into a single "value" column
     ['usa', 'beep'],
     as_=['column', 'value']
).mark_bar().encode(
     x=alt.X('pressed_on:T', timeUnit='date'), # X Axis is a day based time parameter 
     y='value:Q', # Y Axis is the combined USA/Beep Value stack as a Quantatative param
     color='column:N')

# Display the chart data using the altair_chart function from within streamlit
st.altair_chart(c)

# Create a 2nd Pandas DataFrame (dateBasedDF) for the selected date by reading the button_pressed table
dateBasedQuery ="SELECT * from button_pressed where pressed_on LIKE '" + date.strftime("%Y-%m-%d%") + "'"

# Create a DataFrame for a specific day
dateBasedDF = pd.read_sql(dateBasedQuery, con=conn)

# Write out the date from the Button Pressed Date control
st.write("DataFrame for ", date.strftime("%Y-%m-%d"))

# And output the dateBased Data Frame
st.write(dateBasedDF)

# close off the connection to sqlite3
conn.close()
