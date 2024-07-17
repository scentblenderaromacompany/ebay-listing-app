import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter import Canvas, Frame, Scrollbar
import os
import boto3
from botocore.exceptions import NoCredentialsError
from PIL import Image, ImageTk

# Define the CSV headers
headers = [
    "*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)", "CustomLabel", "*Category",
    "StoreCategory", "*Title", "Subtitle", "Relationship", "RelationshipDetails", "*ConditionID",
    "UPC/ISBN/EAN", "Price", "Quantity", "Item Photo URL", "Description", "Format",
    "C:Style", "C:Brand", "C:Type", "C:Theme", "C:Color", "C:Main Stone Color", "C:Pendant Shape",
    "C:Secondary Stone", "C:Metal", "C:Main Stone", "C:Material", "C:Base Metal", "C:Pendant/Locket Type",
    "C:Main Stone Shape", "C:Main Stone Creation", "C:Metal Purity", "C:Country of Origin", "C:Necklace Length",
    "C:Setting Style", "C:Main Stone Treatment", "C:Cut Grade", "C:Number of Gemstones", "C:Chain Type",
    "C:Vintage", "C:Occasion", "C:Closure", "PaymentProfileName", "ShippingProfileName",
    "ReturnProfileName"
]

# Item specifics options for fashion jewelry
item_specifics_options = {
    "C:Style": ["Classic", "Modern", "Vintage", "Bohemian"],
    "C:Brand": ["Brand A", "Brand B", "Brand C"],
    "C:Type": ["Necklace", "Bracelet", "Pendant", "Charm"],
    "C:Theme": ["Love", "Nature", "Religious", "Fashion"],
    "C:Color": ["Gold", "Silver", "Black", "White"],
    "C:Main Stone Color": ["Clear", "Red", "Blue", "Green"],
    "C:Pendant Shape": ["Heart", "Round", "Square", "Oval"],
    "C:Secondary Stone": ["None", "Diamond", "Ruby", "Sapphire"],
    "C:Metal": ["Gold", "Silver", "Platinum", "Stainless Steel"],
    "C:Main Stone": ["Diamond", "Ruby", "Sapphire", "Emerald"],
    "C:Material": ["Metal", "Plastic", "Wood", "Leather"],
    "C:Base Metal": ["Copper", "Brass", "Nickel"],
    "C:Pendant/Locket Type": ["Locket", "Pendant"],
    "C:Main Stone Shape": ["Round", "Oval", "Square", "Heart"],
    "C:Main Stone Creation": ["Natural", "Lab-Created"],
    "C:Metal Purity": ["14k", "18k", "24k"],
    "C:Country of Origin": ["USA", "China", "India", "Italy"],
    "C:Necklace Length": ["16 inches", "18 inches", "20 inches", "22 inches"],
    "C:Setting Style": ["Prong", "Bezel", "Channel"],
    "C:Main Stone Treatment": ["None", "Heated", "Enhanced"],
    "C:Cut Grade": ["Excellent", "Very Good", "Good"],
    "C:Number of Gemstones": ["1", "2", "3", "4"],
    "C:Chain Type": ["Cable", "Rope", "Box"],
    "C:Vintage": ["Yes", "No"],
    "C:Occasion": ["Wedding", "Birthday", "Anniversary"],
    "C:Closure": ["Lobster", "Spring Ring", "Toggle"]
}

# AWS S3 client
s3 = boto3.client('s3')
bucket_name = 'your-s3-bucket-name'

def upload_image_to_s3(image_path):
    object_name = os.path.basename(image_path)
    try:
        s3.upload_file(image_path, bucket_name, object_name)
        return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "The selected file was not found.")
        return None
    except NoCredentialsError:
        messagebox.showerror("Credentials Error", "Credentials not available.")
        return None

def browse_image():
    filenames = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.png")])
    if filenames:
        image_urls = []
        for filename in filenames:
            image_url = upload_image_to_s3(filename)
            if image_url:
                image_urls.append(image_url)
                display_image(filename)
        image_url_entry.insert(0, "|".join(image_urls))

def display_image(image_path):
    img = Image.open(image_path)
    img.thumbnail((100, 100))
    img = ImageTk.PhotoImage(img)
    image_label.config(image=img)
    image_label.image = img

def list_s3_images():
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            return [f"https://{bucket_name}.s3.amazonaws.com/{item['Key']}" for item in response['Contents']]
        else:
            messagebox.showinfo("No Images", "No images found in the S3 bucket.")
            return []
    except NoCredentialsError:
        messagebox.showerror("Credentials Error", "Credentials not available.")
        return []

def select_image_from_s3():
    image_urls = list_s3_images()
    if image_urls:
        selected_image = simpledialog.askstring("Select Image", f"""Available images:
{chr(10).join(image_urls)}

Enter the URL of the image to select:""")
        if selected_image in image_urls:
            image_url_entry.insert(0, selected_image)
        else:
            messagebox.showerror("Invalid Selection", "The entered URL is not valid.")

def save_progress():
    progress = {header: entries[header].get() for header in headers}
    with open('progress.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(progress)
    messagebox.showinfo("Progress Saved", "Your progress has been saved.")

def load_progress():
    if os.path.exists('progress.csv'):
        with open('progress.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            progress = next(reader)
            for header in headers:
                entries[header].delete(0, tk.END)
                entries[header].insert(0, progress[header])
        messagebox.showinfo("Progress Loaded", "Your progress has been loaded.")
    else:
        messagebox.showinfo("No Progress Found", "No saved progress found.")

def bulk_upload():
    bulk_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if bulk_file:
        with open(bulk_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                write_to_csv('ebay_inventory.csv', row)
        messagebox.showinfo("Bulk Upload", "Bulk upload completed successfully!")

def write_to_csv(filename, data):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def validate_input(field_name, value):
    if not value:
        messagebox.showerror("Input Error", f"{field_name} is required.")
        return False
    return True

def save_template():
    template = {header: entries[header].get() for header in headers}
    template_name = simpledialog.askstring("Save Template", "Enter template name:")
    if template_name:
        with open(f"{template_name}.json", mode='w', encoding='utf-8') as file:
            json.dump(template, file)
        messagebox.showinfo("Template Saved", f"Template '{template_name}' has been saved.")

def load_template():
    template_file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if template_file:
        with open(template_file, mode='r', encoding='utf-8') as file:
            template = json.load(file)
            for header in headers:
                entries[header].delete(0, tk.END)
                entries[header].insert(0, template.get(header, ''))
        messagebox.showinfo("Template Loaded", f"Template '{os.path.basename(template_file)}' has been loaded.")

class EbayCSVUploader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("eBay CSV Uploader")
        self.geometry("800x800")

        self.canvas = Canvas(self)
        self.scroll_frame = Frame(self.canvas, bg='#F5DEB3')

        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="self.scroll_frame")

        self.scroll_frame.bind("<Configure>", lambda event, canvas=self.canvas: canvas.configure(scrollregion=canvas.bbox("all")))

        self.create_widgets()

    def create_widgets(self):
        global entries
        entries = {}

        for idx, field in enumerate(headers):
            if field.startswith("C:"):
                label = tk.Label(self.scroll_frame, text=field.split(":")[-1], bg='#F5DEB3')
                label.grid(row=idx, column=0, padx=10, pady=5, sticky=tk.W)
                combobox = ttk.Combobox(self.scroll_frame, values=item_specifics_options[field], state='readonly')
                combobox.grid(row=idx, column=1, padx=10, pady=5)
                entries[field] = combobox
            else:
                label = tk.Label(self.scroll_frame, text=field, bg='#F5DEB3')
                label.grid(row=idx, column=0, padx=10, pady=5, sticky=tk.W)
                entry = tk.Entry(self.scroll_frame, width=50)
                entry.grid(row=idx, column=1, padx=10, pady=5)
                entries[field] = entry

        image_url_label = tk.Label(self.scroll_frame, text="Item Photo URL", bg='#F5DEB3')
        image_url_label.grid(row=len(headers), column=0, padx=10, pady=5, sticky=tk.W)
        global image_url_entry
        image_url_entry = tk.Entry(self.scroll_frame, width=50)
        image_url_entry.grid(row=len(headers), column=1, padx=10, pady=5)

        browse_button = tk.Button(self.scroll_frame, text="Browse", command=browse_image)
        browse_button.grid(row=len(headers), column=2, padx=10, pady=5)

        global image_label
        image_label = tk.Label(self.scroll_frame, bg='#F5DEB3')
        image_label.grid(row=len(headers)+1, column=1, padx=10, pady=5)

        s3_button = tk.Button(self.scroll_frame, text="From S3", command=select_image_from_s3)
        s3_button.grid(row=len(headers)+2, column=1, padx=10, pady=5)

        save_button = tk.Button(self.scroll_frame, text="Save Progress", command=save_progress)
        save_button.grid(row=len(headers)+3, column=0, padx=10, pady=5)

        load_button = tk.Button(self.scroll_frame, text="Load Progress", command=load_progress)
        load_button.grid(row=len(headers)+3, column=1, padx=10, pady=5)

        upload_button = tk.Button(self.scroll_frame, text="Bulk Upload", command=bulk_upload)
        upload_button.grid(row=len(headers)+3, column=2, padx=10, pady=5)

        template_save_button = tk.Button(self.scroll_frame, text="Save Template", command=save_template)
        template_save_button.grid(row=len(headers)+4, column=0, padx=10, pady=5)

        template_load_button = tk.Button(self.scroll_frame, text="Load Template", command=load_template)
        template_load_button.grid(row=len(headers)+4, column=1, padx=10, pady=5)

        submit_button = tk.Button(self.scroll_frame, text="Submit", command=self.submit)
        submit_button.grid(row=len(headers)+5, column=1, padx=10, pady=5)

    def submit(self):
        data = {header: entries[header].get() for header in headers}
        for key, value in data.items():
            if not validate_input(key, value):
                return
        write_to_csv('ebay_inventory.csv', data)
        messagebox.showinfo("Success", "Data has been submitted successfully!")

if __name__ == "__main__":
    app = EbayCSVUploader()
    app.mainloop()
