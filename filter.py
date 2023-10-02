import pandas as pd

file_path = "calendar_dec18.csv"
df = pd.read_csv(file_path)

date_column_name = 'date'

df[date_column_name] = pd.to_datetime(df[date_column_name])

start_date = input("Enter the start date (YYYY-MM-DD): ")
end_date = input("Enter the end date (YYYY-MM-DD): ")

filtered_df = df[(df[date_column_name] >= start_date) & (df[date_column_name] <= end_date)]

filtered_df = filtered_df.sort_values(by=date_column_name, ascending=False)

for _, row in filtered_df.iterrows():
    print(f"Date: {row[date_column_name]}, Listing ID: {row['listing_id']}, Price: {row['price']}")