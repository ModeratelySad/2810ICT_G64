import pandas as pd

file_path = 'listings_dec18.csv'
df = pd.read_csv(file_path)

keyword = input("Enter a keyword: ")

filtered_df = df[df['neighbourhood_cleansed'].str.contains(keyword, case=False)]

if not filtered_df.empty:
    print("Matching records:")
    print(filtered_df)
else:
    print("No matching records found.")