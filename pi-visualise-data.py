<<<<<<< HEAD
import sqlite3 
=======
import sqlite3
>>>>>>> 80db94211802b6b7a38ce0b4fba85b440c1fde54
import pandas as pd
import streamlit as st
import altair as alt

<<<<<<< HEAD
# create a connection to the pi-traffic-lights.db sqlite3 Database
=======
# create a connection to the pi-traffic-lights sqlite3 Database
>>>>>>> 80db94211802b6b7a38ce0b4fba85b440c1fde54
conn = sqlite3.connect('pi-traffic-lights.db')

# create a sidebar date selector
date = st.sidebar.date_input("Button Pressed Date")

<<<<<<< HEAD
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
=======
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
>>>>>>> 80db94211802b6b7a38ce0b4fba85b440c1fde54
     color='column:N')

# Display the chart data using the altair_chart function from within streamlit
st.altair_chart(c)

<<<<<<< HEAD
# Create a 2nd Pandas DataFrame (dateBasedDF) for the selected date by reading the button_pressed table
dateBasedQuery ="SELECT * from button_pressed where pressed_on LIKE '" + date.strftime("%Y-%m-%d%") + "'"

# Create a DataFrame for a specific day
dateBasedDF = pd.read_sql(dateBasedQuery, con=conn)

# Write out the date from the Button Pressed Date control
st.write("DataFrame for ", date.strftime("%Y-%m-%d"))

# And output the dateBased Data Frame
st.write(dateBasedDF)
=======
# Create a SQLite3 query for all the data for a specific day
dateBasedQuery = "SELECT * from button_pressed
                  where pressed_on LIKE
                  '" + date.strftime("%Y-%m-%d%") + "'"

# Create a 2nd Pandas DataFrame for the selected date only
dateBasedData = pd.read_sql(dateBasedQuery, con=conn)

st.write("DataFrame for ", date.strftime("%Y-%m-%d"))
st.write(dateBasedData)
>>>>>>> 80db94211802b6b7a38ce0b4fba85b440c1fde54

# close off the connection to sqlite3
conn.close()
