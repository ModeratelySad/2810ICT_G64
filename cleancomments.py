import pandas as pd
import re

# Load data from CSV files
listings = pd.read_csv('listings_dec18.csv', low_memory=False)
reviews = pd.read_csv('reviews_dec18.csv')

# Merge data
merged_data = reviews.merge(listings[['id']], how='inner', left_on='listing_id', right_on='id')

# Define cleanliness-related keywords
cleanliness_keywords = ['clean', 'tidy', 'spotless', 'dirt', 'dust', 'hygiene', 'sanitize', 'neat']

# Function to check if a comment contains cleanliness-related keywords
def has_cleanliness_keywords(comment):
    if isinstance(comment, str):
        comment = comment.lower()
        for keyword in cleanliness_keywords:
            if re.search(r'\b{}\b'.format(keyword), comment):
                return True
    return False


# Apply the function to the comments and create a new column 'cleanliness_comment'
merged_data['cleanliness_comment'] = merged_data['comments'].apply(has_cleanliness_keywords)

# Count the number of reviews with cleanliness-related comments
cleanliness_comment_count = merged_data['cleanliness_comment'].sum()

print("Number of customers commenting on cleanliness:", cleanliness_comment_count)