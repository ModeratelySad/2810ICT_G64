import tkinter as tk
from tkinter import ttk, filedialog, Text, messagebox, scrolledtext
from tkcalendar import DateEntry
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
    selected_file = file_combobox.get()
    try:
        data = pd.read_csv(selected_file, low_memory=False)
        data['cleanliness_comment'] = data['comments'].apply(has_cleanliness_keywords)
        cleanliness_comment_count = data['cleanliness_comment'].sum()
        messagebox.showinfo("Cleanliness Comments", f"Number of cleanliness comments: {cleanliness_comment_count}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def filter_by_suburb():
    keyword = suburb_entry.get()
    file_path = 'listings_dec18.csv'
    df = pd.read_csv(file_path)
    filtered_df = df[df['neighbourhood_cleansed'].str.contains(keyword, case=False)]
    result_text.delete(1.0, tk.END)
    if not filtered_df.empty:
        result_text.insert(tk.END, "Matching records:\n")
        result_text.insert(tk.END, filtered_df.to_string())
    else:
        result_text.insert(tk.END, "No matching records found.")

def plot_price_distribution():
    global current_canvas
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
        if current_canvas:
            current_canvas.get_tk_widget().destroy()
        current_canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        current_canvas.get_tk_widget().pack()
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
        result = selected_period.merge(keyword_matches, left_on='listing_id', right_on='id', how='inner')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, result.to_string())
    else:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No 'id' column found in listings_data. Please check the column names.")

def filter_by_date():
    start_date = date_start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = date_end_date_entry.get_date().strftime('%Y-%m-%d')
    filtered_df = calendar_data[(calendar_data[date_column_name] >= start_date) & (calendar_data[date_column_name] <= end_date)]
    filtered_df = filtered_df.sort_values(by=date_column_name, ascending=False)
    result_text.delete(1.0, tk.END)
    for _, row in filtered_df.iterrows():
        result_text.insert(tk.END, f"Date: {row[date_column_name]}, Listing ID: {row['listing_id']}, Price: {row['price']}\n")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analysis Tool")

        self.nav_frame = tk.Frame(self.root, bg="gray")
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

        global canvas_frame
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def show_clean_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        ttk.Label(canvas_frame, text="Select File:").pack(pady=10)
        global file_combobox
        file_combobox = ttk.Combobox(canvas_frame, values=["reviews_dec18.csv"])
        file_combobox.pack(pady=10)
        check_button = ttk.Button(canvas_frame, text="Check Cleanliness Comments", command=check_cleanliness_comments)
        check_button.pack(pady=20)

    def show_suburb_canvas(self):
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        ttk.Label(canvas_frame, text="Enter a keyword:").pack(pady=10)
        global suburb_entry
        suburb_entry = ttk.Entry(canvas_frame, width=50)
        suburb_entry.pack(pady=10)
        filter_button = ttk.Button(canvas_frame, text="Filter by Suburb", command=filter_by_suburb)
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

if __name__ == "__main__":
    calendar_data = pd.read_csv('calendar_dec18.csv')
    date_column_name = 'date'
    calendar_data[date_column_name] = pd.to_datetime(calendar_data[date_column_name])
    listings_data = pd.read_csv('listings_dec18.csv')
    root = tk.Tk()
    app = App(root)
    root.mainloop()
