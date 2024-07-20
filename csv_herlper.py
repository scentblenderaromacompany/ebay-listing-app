import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import logging
import coloredlogs

# Setup logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
coloredlogs.install(level='DEBUG', fmt=LOG_FORMAT)

# Path to the CSV file
CSV_FILE_PATH = '/home/robertmcasper/ebay-listing-app/CSV/listings.csv'

# Define the CSV headers
headers = [
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

# Item specifics options for fashion jewelry (expanded from eBay and Amazon)
item_specifics_options = {
    "Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)": ["Draft"],
    "Custom label (SKU)": ["Label1", "Label2", "Label3", "Label4"],
    "*Category": ["155101", "50647", "50637", "110633"],  # Necklace, earrings, bracelets, handmade
    "Title": ["Test Draft Shoe", "Test Draft Necklace", "Test Draft Earrings", "Test Draft Bracelet"],
    "UPC": ["Does not apply", "UPC1", "UPC2", "UPC3"],
    "Price": ["10", "20", "30", "40", "50"],
    "Quantity": ["1", "2", "3", "4", "5"],
    "Item photo URL": ["https://ir.ebaystatic.com/cr/v/c1/rsc/ebay_logo_512.png", "URL2", "URL3", "URL4"],
    "Condition ID": ["1000", "1500", "1750", "2000", "2500", "3000", "4000", "5000", "6000", "7000"],  # Valid eBay Condition IDs
    "Description": [],
    "Format": ["FixedPrice", "Auction"]
}

class EbayCSVUploader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("eBay CSV Uploader")
        self.geometry("400x600")
        self.current_field_index = 0
        self.listing_data = []
        self.title_text = ""

        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use the 'clam' theme for a more modern look
        self.configure_style()

        self.create_widgets()

    def configure_style(self):
        self.style.configure('TFrame', background='#2E4053')
        self.style.configure('TLabel', background='#2E4053', foreground='#F7F9F9', font=('Helvetica', 14, 'bold'))
        self.style.configure('TCombobox', fieldbackground='#F7F9F9', background='#34495E', foreground='#2E4053', font=('Helvetica', 12))
        self.style.map('TCombobox', fieldbackground=[('readonly', '#F7F9F9')], background=[('readonly', '#34495E')], foreground=[('readonly', '#2E4053')])
        self.style.configure('TButton', background='#1ABC9C', foreground='#F7F9F9', font=('Helvetica', 12, 'bold'))
        self.style.map('TButton', background=[('active', '#16A085')])

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, style='TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        self.combo_label = ttk.Label(self.main_frame, text=headers[self.current_field_index], style='TLabel')
        self.combo_label.pack(pady=10)

        self.combo_box = ttk.Combobox(self.main_frame, values=item_specifics_options.get(headers[self.current_field_index], []), style='TCombobox')
        self.combo_box.pack(pady=10)
        self.combo_box.bind("<Return>", self.next_field)
        self.combo_box.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.combo_box.bind("<KeyRelease>", self.on_key_release)

        self.complete_button = ttk.Button(self.main_frame, text="Complete Listing", command=self.complete_listing, style='TButton')
        self.complete_button.pack(pady=20)

    def on_combobox_select(self, event):
        if headers[self.current_field_index] == "Title":
            self.title_text = self.combo_box.get()

    def on_key_release(self, event):
        if self.current_field_index < len(headers) and headers[self.current_field_index] == "Title":
            self.title_text = self.combo_box.get()

    def next_field(self, event):
        if self.current_field_index >= len(headers):
            return

        value = self.combo_box.get()
        if headers[self.current_field_index] == "Title":
            self.title_text = value
        elif headers[self.current_field_index] == "Description":
            value = self.title_text

        self.listing_data.append(value)
        logging.debug(f"Field: {headers[self.current_field_index]}, Value: {value}")
        self.combo_box.delete(0, tk.END)  # Clear the combobox

        self.current_field_index += 1

        if self.current_field_index < len(headers):
            self.combo_label.config(text=headers[self.current_field_index])
            self.combo_box.config(values=item_specifics_options.get(headers[self.current_field_index], []))
            self.combo_box.set('')  # Clear the current value in the combobox
            self.combo_box.pack()
            self.combo_label.pack()
            self.combo_box.focus_set()
        else:
            self.complete_listing()

    def complete_listing(self):
        self.save_listing()
        if messagebox.askyesno("Add Another Listing", "Do you want to add another listing?"):
            self.reset_form()
        else:
            self.quit()

    def save_listing(self):
        try:
            file_exists = os.path.exists(CSV_FILE_PATH)
            with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(headers)  # Write headers if file doesn't exist
                writer.writerow(self.listing_data)
            logging.info(f"Listing saved: {self.listing_data}")
            self.listing_data = []  # Clear listing data after saving
        except Exception as e:
            logging.error(f"Failed to save listing: {e}")

    def reset_form(self):
        self.listing_data = []
        self.current_field_index = 0
        self.combo_label.config(text=headers[self.current_field_index])
        self.combo_box.config(values=item_specifics_options.get(headers[self.current_field_index], []))
        self.combo_box.set('')  # Clear the current value in the combobox
        self.combo_label.pack()
        self.combo_box.pack()
        self.combo_box.focus_set()

if __name__ == "__main__":
    app = EbayCSVUploader()
    app.mainloop()
