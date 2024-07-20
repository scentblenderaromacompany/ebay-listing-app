# main.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
import csv
import os
import logging

class ColorFormatter(logging.Formatter):
    def __init__(self, fmt="%(levelname)s: %(message)s"):
        super().__init__(fmt)
        self.FORMATS = {
            logging.DEBUG: "\033[37m" + fmt + "\033[0m",
            logging.INFO: "\033[36m" + fmt + "\033[0m",
            logging.WARNING: "\033[33m" + fmt + "\033[0m",
            logging.ERROR: "\033[31m" + fmt + "\033[0m",
            logging.CRITICAL: "\033[41m" + fmt + "\033[0m",
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Configure logging
logger = logging.getLogger("CSVFillerApp")
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class CSVFillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Filler for eBay Listings")
        self.root.configure(bg='lightblue')
        self.root.attributes('-topmost', True)  # Keep the window always on top

        # Periodically ensure the window stays on top
        self.root.after(1000, self.keep_on_top)

        # Define the columns based on the provided template
        self.columns = [
            "Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)", 
            "Custom label (SKU)", 
            "Category ID", 
            "Title", 
            "UPC", 
            "Price", 
            "Quantity", 
            "Item photo URL", 
            "Condition ID", 
            "Description", 
            "Format"
        ]
        self.options = {
            "Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)": ["Draft"],
            "Custom label (SKU)": ["SKU1", "SKU2", "SKU3"],
            "Category ID": [
                "155101 - Necklaces & Pendants",
                "50637 - Bracelets",
                "67681 - Rings",
                "110633 - Handcrafted & Artisan Jewelry",
                "50647 - Earrings"
            ],
            "Title": ["Sample Title 1", "Sample Title 2", "Sample Title 3"],
            "UPC": ["123456789012", "234567890123", "345678901234"],
            "Price": ["10.99", "15.99", "20.99"],
            "Quantity": ["1", "2", "3"],
            "Item photo URL": ["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"],
            "Condition ID": ["NEW", "USED", "REFURBISHED"],
            "Description": ["Sample Description 1", "Sample Description 2"],
            "Format": ["FixedPrice", "Auction"]
        }
        self.current_column = 0
        self.entries = []
        self.data = []
        self.title_value = ""  # To store the title for description

        self.label = tk.Label(root, text=f"Enter {self.columns[self.current_column]}:", font=('Helvetica', 20, 'bold'), fg='black', bg='lightblue')
        self.label.pack(pady=10)

        self.entry = ttk.Combobox(root, font=('Helvetica', 20, 'bold'), values=self.options[self.columns[self.current_column]], state='normal')
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.save_entry)
        self.entry.bind('<KeyRelease>', self.limit_title_length)
        self.entry.focus()

        self.load_templates()
        logger.info("CSVFillerApp initialized")

    def keep_on_top(self):
        self.root.attributes('-topmost', True)
        self.root.after(1000, self.keep_on_top)

    def limit_title_length(self, event):
        if self.columns[self.current_column] == "Title":
            current_text = self.entry.get()
            if len(current_text) > 80:
                self.entry.set(current_text[:80])
                messagebox.showwarning("Title Length Exceeded", "Title cannot exceed 80 characters.")

    def save_entry(self, event):
        value = self.entry.get().strip()
        if self.columns[self.current_column] == "Title":
            self.title_value = value  # Save title to copy to description

        self.entries.append(value)
        self.entry.delete(0, tk.END)
        self.current_column += 1

        if self.current_column < len(self.columns):
            # If the current column is "Description", auto-fill it with the "Title" entry
            if self.columns[self.current_column] == "Description":
                self.entry.insert(0, self.title_value)  # Title is saved in title_value

            self.label.config(text=f"Enter {self.columns[self.current_column]}:")
            self.entry.config(values=self.options[self.columns[self.current_column]])
        else:
            self.data.append(self.entries)
            self.entries = []
            self.current_column = 0
            self.label.config(text=f"Enter {self.columns[self.current_column]}:")
            self.entry.config(values=self.options[self.columns[self.current_column]])
            self.ask_for_another_listing()

    def ask_for_another_listing(self):
        if messagebox.askyesno("Add Another Listing?", "Do you want to add another listing?"):
            logger.info("User chose to add another listing")
            self.entry.focus()
        else:
            self.save_to_csv()
            self.ask_to_save_template()
            logger.info("Exiting application")
            self.root.quit()

    def ask_to_save_template(self):
        if messagebox.askyesno("Save Template?", "Do you want to save this listing as a template?"):
            template_name = simpledialog.askstring("Template Name", "Enter a name for this template:")
            if template_name:
                self.save_template(template_name)
                logger.info(f"Template {template_name} saved")

    def save_template(self, template_name):
        if not os.path.exists("templates"):
            os.makedirs("templates")
        with open(f"templates/{template_name}.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.columns)
            writer.writerows(self.data)

    def save_to_csv(self):
        directory = "/home/robertmcasper/ebay-listing-app/CSV/output"
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, "listings.csv")
        if not os.path.exists(file_path):
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(self.columns)
                logger.info("Created new listings.csv file")
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(self.data)
            logger.info("Saved data to listings.csv")

    def load_templates(self):
        if not os.path.exists("templates"):
            os.makedirs("templates")
        self.templates = [f for f in os.listdir("templates") if f.endswith(".csv")]
        if self.templates:
            if messagebox.askyesno("Load Template?", "Do you want to load a template?"):
                template = simpledialog.askstring("Select Template", f"Available Templates: {', '.join(self.templates)}")
                if template and f"{template}.csv" in self.templates:
                    self.load_template(template)
                    logger.info(f"Loaded template: {template}")

    def load_template(self, template_name):
        with open(f"templates/{template_name}.csv", "r") as file:
            reader = csv.reader(file)
            self.columns = next(reader)
            self.data = list(reader)

        self.current_column = 0
        self.entries = []

        self.label.config(text=f"Enter {self.columns[self.current_column]}:")
        self.entry.delete(0, tk.END)
        self.entry.config(values=self.options[self.columns[self.current_column]])
        self.entry.bind("<Return>", self.save_entry)
        logger.info("Template loaded and entry fields initialized")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVFillerApp(root)
    root.mainloop()
    logger.info("Application closed")
