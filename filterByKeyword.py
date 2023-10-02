import pandas as pd
import re

calendar_data = pd.read_csv('calendar_dec18.csv')
listings_data = pd.read_csv('listings_dec18.csv')

start_date = input("Enter the start date (YYYY-MM-DD): ")
end_date = input("Enter the end date (YYYY-MM-DD): ")

selected_period = calendar_data[(calendar_data['date'] >= start_date) & (calendar_data['date'] <= end_date)]

keyword = input("Enter a keyword to search for: ")

escaped_keyword = re.escape(keyword)

keyword_matches = listings_data[listings_data['name'].str.contains(escaped_keyword, case=False, na=False) |
                                listings_data['description'].str.contains(escaped_keyword, case=False, na=False)]

if 'id' in listings_data.columns:
    result = selected_period.merge(keyword_matches, left_on='listing_id', right_on='id', how='inner')
else:
    print("No 'id' column found in listings_data. Please check the column names.")

print(result)