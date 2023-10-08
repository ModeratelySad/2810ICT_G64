import tkinter as tk
from tkinter import ttk, filedialog, Text, messagebox, scrolledtext
from tkcalendar import DateEntry
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
from datetime import datetime

# Define cleanliness-related keywords
cleanliness_keywords = ['clean', 'tidy', 'spotless', 'dirt', 'dust', 'hygiene', 'sanitize', 'neat']

# Global variable to store the current canvas (if it exists)
current_canvas = None


def has_cleanliness_keywords(comment):
    if isinstance(comment, str):
        comment = comment.lower()
        for keyword in cleanliness_keywords:
            if re.search(r'\b{}\b'.format(keyword), comment):
                return True
    return False


def check_cleanliness_comments():
    selected_file = 'reviews_dec18.csv'
    try:
        data = pd.read_csv(selected_file, low_memory=False)
        data['cleanliness_comment'] = data['comments'].apply(has_cleanliness_keywords)
        cleanliness_comment_count = data['cleanliness_comment'].sum()
        messagebox.showinfo("Cleanliness Comments", f"Number of cleanliness comments: {cleanliness_comment_count}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def filter_by_suburb(keyword):
    file_path = 'listings_dec18.csv'
    df = pd.read_csv(file_path)
    filtered_df = df[df['neighbourhood_cleansed'].str.contains(keyword, case=False)]

    # Create a new Toplevel window
    result_window = tk.Toplevel(root)
    result_window.title("Filtered Results")

    # Create a Treeview widget to display the data
    result_tree = ttk.Treeview(result_window, columns=["Listing IDs"], show="headings")
    result_tree.heading("Listing IDs", text="Listing IDs")

    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            result_tree.insert("", "end", values=(str(row['id'])))

        result_tree.pack()
    else:
        result_text = tk.Label(result_window, text="No matching records found.")
        result_text.pack()


def plot_price_distribution():
    start_date = start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = end_date_entry.get_date().strftime('%Y-%m-%d')

    try:
        calendar_data = pd.read_csv('calendar_dec18.csv')
        filtered_data = calendar_data[(calendar_data['date'] >= start_date) & (calendar_data['date'] <= end_date)]
        filtered_data['price'] = filtered_data['price'].str.replace('$', '').str.replace(',', '').astype(float)
        fig, ax = plt.subplots()
        ax.hist(filtered_data['price'], bins=30, edgecolor='black', range=(0, 600))
        ax.set_title('Distribution of Property Prices')
        ax.set_xlabel('Price ($)')
        ax.set_ylabel('Frequency')

        # Create a new Toplevel window to display the plot
        plot_window = tk.Toplevel(root)
        plot_window.title('Price Distribution Plot')
        plot_canvas = FigureCanvasTkAgg(fig, master=plot_window)
        plot_canvas.get_tk_widget().pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def filter_by_keyword():
    start_date = keyword_start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = keyword_end_date_entry.get_date().strftime('%Y-%m-%d')

    selected_period = calendar_data[(calendar_data['date'] >= start_date) & (calendar_data['date'] <= end_date)]

    keyword = keyword_filter_entry.get()
    escaped_keyword = re.escape(keyword)

    keyword_matches = listings_data[listings_data['name'].str.contains(escaped_keyword, case=False, na=False) |
                                    listings_data['description'].str.contains(escaped_keyword, case=False, na=False)]

    if 'id' in listings_data.columns:
        # Create a new Toplevel window
        result_window = tk.Toplevel()
        result_window.title("Search Result")

        # Create a text widget to display the result
        result_text = tk.Text(result_window, wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True)

        # Extract and format the matching listing IDs in a table
        matching_listing_ids = keyword_matches['id'].tolist()
        if matching_listing_ids:
            table_data = {'Listing ID': matching_listing_ids}
            result_df = pd.DataFrame(table_data)

            # Center-align and format the text
            result_text.insert(tk.END, "Listings Containing '{}'\n".format(keyword))
            result_text.tag_configure('center', justify='center')
            result_text.tag_add('center', '1.0', 'end')

            # Apply font formatting (bigger size and bold)
            result_text.tag_configure('bold', font=('Helvetica', 14, 'bold'))
            result_text.tag_add('bold', '1.0', '1.end')

            # Display the DataFrame
            result_text.insert(tk.END, result_df.to_string(index=False))
        else:
            result_text.insert(tk.END, "No listings containing '{}' found.".format(keyword))


def filter_by_date():
    start_date = date_start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = date_end_date_entry.get_date().strftime('%Y-%m-%d')
    filtered_df = calendar_data[
        (calendar_data[date_column_name] >= start_date) & (calendar_data[date_column_name] <= end_date)]
    filtered_df = filtered_df.sort_values(by=date_column_name, ascending=False)

    # Create a new Toplevel window
    new_window = tk.Toplevel(root)
    new_window.title("Filtered Data")

    # Create a ttk.Treeview widget for displaying the table
    table = ttk.Treeview(new_window, columns=("Date", "Listing ID", "Price"), show="headings")
    table.heading("Date", text="Date")
    table.heading("Listing ID", text="Listing ID")
    table.heading("Price", text="Price")

    # Populate the table with the filtered data
    for _, row in filtered_df.iterrows():
        table.insert("", "end", values=(row[date_column_name], row['listing_id'], row['price']))

    # Add a scrollbar to the table
    table_scrollbar = ttk.Scrollbar(new_window, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=table_scrollbar.set)

    # Pack the table
    table.pack(fill="both", expand=True)
    table_scrollbar.pack(side="right", fill="y")



def advanced_filter_and_sort():
    try:
        min_price = float(min_price_entry.get())
        max_price = float(max_price_entry.get())
        min_review_score = float(min_review_score_entry.get())

        sort_by = sort_by_combobox.get()

        # Ensure 'price' and 'review_scores_rating' are in the correct format
        # Convert to string, handle non-string data, then convert to float
        listings_data['price'] = pd.to_numeric(
            listings_data['price'].str.replace('$', '').str.replace(',', ''), errors='coerce')
        listings_data['review_scores_rating'] = pd.to_numeric(listings_data['review_scores_rating'], errors='coerce')

        filtered_data = listings_data[
            (listings_data['price'] >= min_price) &
            (listings_data['price'] <= max_price) &
            (listings_data['review_scores_rating'] >= min_review_score)
        ]

        sorted_data = filtered_data.sort_values(by=sort_by, ascending=ascending_var.get() == 1)

        # Limiting to 10 rows for brevity and select relevant columns
        limited_data = sorted_data.head(10)[['id','name', 'price', 'review_scores_rating', 'neighbourhood_cleansed']]

        # Formatting results
        limited_data['price'] = limited_data['price'].apply(lambda x: f"${x:,.2f}")

        # Create a new top-level window to display the results
        result_window = tk.Toplevel(root)
        result_window.title("Filtered and Sorted Results")

        # Create a Treeview widget to display the results in a table
        columns = ['id','Name', 'Price', 'Review Score', 'Neighbourhood']
        tree = ttk.Treeview(result_window, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(padx=10, pady=10)

        for index, row in limited_data.iterrows():
            tree.insert('', 'end', values=(row['id'], row['name'], row['price'], row['review_scores_rating'], row['neighbourhood_cleansed']))

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for filtering and sorting.")
    except Exception as e:
        messagebox.showerror("Error", str(e))



def search_by_listing_id():
    listing_id = search_entry.get()  # Get the listing ID from the input field
    if not listing_id:
        messagebox.showwarning("Search Error", "Please enter a Listing ID to search.")
        return

    try:
        listings_data = pd.read_csv('listings_dec18.csv')
        if 'id' in listings_data.columns:
            result_df = listings_data[listings_data['id'] == int(listing_id)]
            if not result_df.empty:
                # Create a new Toplevel window
                result_window = tk.Toplevel(root)
                result_window.title("Search Result")

                # Create a text widget to display the result
                result_text = tk.Text(result_window, wrap=tk.WORD)
                result_text.pack(fill=tk.BOTH, expand=True)

                # Display the result
                result_text.insert(tk.END, "Search Result for Listing ID {}\n\n".format(listing_id))
                result_text.insert(tk.END, result_df.to_string(index=False))
            else:
                messagebox.showinfo("Search Result", "No listings found for Listing ID {}".format(listing_id))
        else:
            messagebox.showerror("Data Error", "Listing IDs are not available in the data.")
    except Exception as e:
        messagebox.showerror("Error", str(e))




class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Welcome to Airbnb Explorer")

        # Title and subtitle labels
        title_label = tk.Label(root, text="Welcome to Airbnb Explorer", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)

        subtitle_label = tk.Label(root, text="Discover the best listings tailored for you!", font=("Helvetica", 16))
        subtitle_label.pack(pady=10)
        # Search bar and button
        search_frame = tk.Frame(root)
        search_frame.pack(pady=20)

        # Create a search entry field
        self.search_entry = ttk.Entry(search_frame, width=50, font=("Helvetica", 14), justify="center")
        self.search_entry.insert(0, "Search Listing ID")
        self.search_entry.pack(side="left", padx=(0, 10))

        # Create a search button
        search_button = tk.Button(search_frame, text="Search", command=self.search_by_listing_id, bg="green",
                                  fg="white",
                                  font=("Helvetica", 14))
        search_button.pack(side="right")

        software_description = tk.Text(root, wrap="word", width=60, height=10, font=("Helvetica", 12), borderwidth=0,
                                       relief="flat")
        software_description.insert(tk.END,
                                    "Welcome to Airbnb Explorer! This software allows you to explore Airbnb listings and find the perfect accommodations for your needs. You can search for listings use this software to view price distribution ghraphs between two dates. You are also able to filter listings between two dates and seacrh for relative 'keywords' or how many people have reffered to cleanliness in listing comments. Thank you for using Airbnb Explorer.")
        software_description.tag_configure("center", justify='center')  # Center-align the text
        software_description.tag_add("center", "1.0", "end")  # Apply center alignment to the entire text
        software_description.pack(pady=20)

        # Canvas for plotting
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.nav_frame = tk.Frame(self.root, bg="green")
        self.nav_frame.pack(side="top", fill="x")

        self.clean_button = tk.Button(self.nav_frame, text="Check Cleanliness", command=self.show_clean_canvas)
        self.clean_button.pack(side="left", padx=10, pady=20)

        self.suburb_button = tk.Button(self.nav_frame, text="Filter by Suburb", command=self.show_suburb_canvas)
        self.suburb_button.pack(side="left", padx=10, pady=20)

        self.plot_button = tk.Button(self.nav_frame, text="Plot Price Distribution", command=self.show_plot_canvas)
        self.plot_button.pack(side="left", padx=10, pady=20)

        self.keyword_button = tk.Button(self.nav_frame, text="Filter by Keyword", command=self.show_keyword_canvas)
        self.keyword_button.pack(side="left", padx=10, pady=20)

        self.date_button = tk.Button(self.nav_frame, text="Filter by Date", command=self.show_date_canvas)
        self.date_button.pack(side="left", padx=10, pady=20)


        self.advanced_filter_sort_button = tk.Button(self.nav_frame, text="Advanced Filter & Sort",
                                                     command=self.show_advanced_filter_and_sort_canvas)
        self.advanced_filter_sort_button.pack(side="left", padx=10, pady=20)


        global canvas_frame
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(pady=20, padx=20, fill="both", expand=True)



    def search_by_listing_id(self):
        listing_id = self.search_entry.get()  # Get the listing ID from the input field
        if not listing_id:
            messagebox.showwarning("Search Error", "Please enter a Listing ID to search.")
            return

        try:
            listings_data = pd.read_csv('listings_dec18.csv')
            selected_columns = [
                'id', 'listing_url', 'name', 'summary', 'space', 'description', 'host_name', 'property_type',
                'room_type', 'accommodates', 'bathrooms', 'bedrooms', 'beds', 'price', 'review_scores_rating'
            ]  # Add your selected columns here

            if 'id' in listings_data.columns:
                result_df = listings_data[listings_data['id'] == int(listing_id)][selected_columns]
                if not result_df.empty:
                    # Create a new Toplevel window
                    result_window = tk.Toplevel(self.root)
                    result_window.title("Search Result")

                    # Create a Treeview widget with the custom style to display the result as a table
                    result_tree = ttk.Treeview(result_window, style="Custom.Treeview")
                    result_tree['columns'] = selected_columns

                    # Add columns to the Treeview
                    for col in selected_columns:
                        result_tree.column(col, width=100)
                        result_tree.heading(col, text=col)

                    # Insert data into the Treeview
                    for index, row in result_df.iterrows():
                        result_tree.insert("", "end", values=list(row))

                    result_tree.pack(fill="both", expand=True)

                else:
                    messagebox.showinfo("Search Result", "No listings found for Listing ID {}".format(listing_id))
            else:
                messagebox.showerror("Data Error", "Listing IDs are not available in the data.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_clean_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        check_button = ttk.Button(canvas_frame, text="Check Cleanliness Comments", command=check_cleanliness_comments)
        check_button.pack(pady=20)

    def show_suburb_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()

        ttk.Label(canvas_frame, text="Select a suburb:").pack(pady=10)

        # Create a list of suburb options
        suburbs = ["Auburn", "Blacktown", "Botany Bay", "Canada Bay", "Canterbury", "City Of Kogarah", "Hornsby",
                   "Lane Cove", "Ku-Ring-Gai", "Leichhardt", "Manly", "Marrickville", "Mosman", "North Sydney",
                   "Penrith", "Pittwater", "Randwick", "Rockdale", "Ryde", "Sutherland Shire", "Sydney",
                   "The Hills Shire", "Warringah", "Waverley", "Willoughby", "Woollahra"
                   ]  # Replace with your actual suburb options

        suburb_combobox = ttk.Combobox(canvas_frame, values=suburbs, width=50)
        suburb_combobox.pack(pady=10)

        def filter_button_clicked():
            selected_suburb = suburb_combobox.get()
            filter_by_suburb(selected_suburb)

        filter_button = ttk.Button(canvas_frame, text="Filter by Suburb", command=filter_button_clicked)
        filter_button.pack(pady=10)

        global result_text
        result_text = scrolledtext.ScrolledText(canvas_frame, wrap="word", height=10, width=50)
        result_text.pack(pady=20)

    def show_plot_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        ttk.Label(canvas_frame, text="Start Date:").pack(padx=10, pady=5)
        global start_date_entry
        start_date_entry = DateEntry(canvas_frame)
        start_date_entry.pack(padx=10, pady=5)
        ttk.Label(canvas_frame, text="End Date:").pack(padx=10, pady=5)
        global end_date_entry
        end_date_entry = DateEntry(canvas_frame)
        end_date_entry.pack(padx=10, pady=5)
        plot_button = ttk.Button(canvas_frame, text="Plot", command=plot_price_distribution)
        plot_button.pack(padx=10, pady=20)

    def show_keyword_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        ttk.Label(canvas_frame, text="Start Date:").pack(padx=10, pady=5)
        global keyword_start_date_entry
        keyword_start_date_entry = DateEntry(canvas_frame)
        keyword_start_date_entry.pack(padx=10, pady=5)
        ttk.Label(canvas_frame, text="End Date:").pack(padx=10, pady=5)
        global keyword_end_date_entry
        keyword_end_date_entry = DateEntry(canvas_frame)
        keyword_end_date_entry.pack(padx=10, pady=5)
        ttk.Label(canvas_frame, text="Enter a keyword:").pack(padx=10, pady=5)
        global keyword_filter_entry
        keyword_filter_entry = ttk.Entry(canvas_frame)
        keyword_filter_entry.pack(padx=10, pady=5)
        keyword_button = ttk.Button(canvas_frame, text="Filter by Keyword", command=filter_by_keyword)
        keyword_button.pack(padx=10, pady=20)
        global result_text
        result_text = scrolledtext.ScrolledText(canvas_frame, wrap="word", height=10, width=50)
        result_text.pack(pady=20)

    def show_date_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        ttk.Label(canvas_frame, text="Start Date:").pack(padx=10, pady=5)
        global date_start_date_entry
        date_start_date_entry = DateEntry(canvas_frame)
        date_start_date_entry.pack(padx=10, pady=5)
        ttk.Label(canvas_frame, text="End Date:").pack(padx=10, pady=5)
        global date_end_date_entry
        date_end_date_entry = DateEntry(canvas_frame)
        date_end_date_entry.pack(padx=10, pady=5)
        date_filter_button = ttk.Button(canvas_frame, text="Filter by Date", command=filter_by_date)
        date_filter_button.pack(padx=10, pady=20)
        global result_text
        result_text = scrolledtext.ScrolledText(canvas_frame, wrap="word", height=10, width=50)
        result_text.pack(pady=20)

    def show_advanced_filter_and_sort_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()

        ttk.Label(canvas_frame, text="Min Price:").pack(pady=5)
        global min_price_entry
        min_price_entry = ttk.Entry(canvas_frame)
        min_price_entry.pack(pady=5)

        ttk.Label(canvas_frame, text="Max Price:").pack(pady=5)
        global max_price_entry
        max_price_entry = ttk.Entry(canvas_frame)
        max_price_entry.pack(pady=5)

        ttk.Label(canvas_frame, text="Min Review Score:").pack(pady=5)
        global min_review_score_entry
        min_review_score_entry = ttk.Entry(canvas_frame)
        min_review_score_entry.pack(pady=5)

        ttk.Label(canvas_frame, text="Sort by:").pack(pady=5)
        global sort_by_combobox
        sort_by_combobox = ttk.Combobox(canvas_frame, values=["price", "review_scores_rating"])
        sort_by_combobox.pack(pady=5)

        global ascending_var
        ascending_var = tk.IntVar()
        ascending_checkbox = ttk.Checkbutton(canvas_frame, text="Sort Ascending", variable=ascending_var)
        ascending_checkbox.pack(pady=5)

        filter_sort_button = ttk.Button(canvas_frame, text="Filter and Sort", command=advanced_filter_and_sort)
        filter_sort_button.pack(pady=20)

        global result_text
        result_text = scrolledtext.ScrolledText(canvas_frame, wrap="word", height=10, width=50)
        result_text.pack(pady=20)


if __name__ == "__main__":
    calendar_data = pd.read_csv('calendar_dec18.csv')
    date_column_name = 'date'
    calendar_data[date_column_name] = pd.to_datetime(calendar_data[date_column_name])
    listings_data = pd.read_csv('listings_dec18.csv')
    root = tk.Tk()
    app = App(root)
    root.mainloop()