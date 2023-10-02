import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to plot price distribution from chart.py
def plot_price_distribution():
    start_date = start_date_entry.get_date().strftime('%Y-%m-%d')
    end_date = end_date_entry.get_date().strftime('%Y-%m-%d')

    try:
        calendar_data = pd.read_csv('calendar_dec18.csv')

        # Filter data based on the selected date range
        filtered_data = calendar_data[(calendar_data['date'] >= start_date) & (calendar_data['date'] <= end_date)]

        # Convert price column to numeric after removing the dollar sign
        filtered_data['price'] = filtered_data['price'].str.replace('$', '').str.replace(',', '').astype(float)

        # Plotting
        fig, ax = plt.subplots()
        ax.hist(filtered_data['price'], bins=30, edgecolor='black', range=(0, 600))
        ax.set_title('Distribution of Property Prices')
        ax.set_xlabel('Price ($)')
        ax.set_ylabel('Frequency')

        # Displaying the plot in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack()
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ==================== MAIN GUI ====================

# Initialize Tkinter
window = tk.Tk()
window.title("Data Analysis Tool")

# Dropdown to select CSV file
ttk.Label(window, text="Select a CSV file:").pack(padx=10, pady=5)
file_combobox = ttk.Combobox(window, values=["listings_dec18.csv", "reviews_dec18.csv", "calendar_dec18.csv"])
file_combobox.set("Select a CSV file")
file_combobox.pack(padx=10, pady=5)

# Date Entry fields for start and end dates
ttk.Label(window, text="Start Date:").pack(padx=10, pady=5)
start_date_entry = DateEntry(window, year=2018, month=1, day=1, date_pattern='yyyy-mm-dd')
start_date_entry.pack(padx=10, pady=5)

ttk.Label(window, text="End Date:").pack(padx=10, pady=5)
end_date_entry = DateEntry(window, year=2019, month=12, day=31, date_pattern='yyyy-mm-dd')
end_date_entry.pack(padx=10, pady=5)

# Keyword entry
ttk.Label(window, text="Enter a keyword:").pack(padx=10, pady=5)
keyword_entry = ttk.Entry(window)
keyword_entry.pack(padx=10, pady=5)

# Buttons for each feature
ttk.Button(window, text="Plot Price Distribution", command=plot_price_distribution).pack(padx=10, pady=5)

window.mainloop()