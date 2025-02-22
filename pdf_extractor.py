import fitz  # PyMuPDF: This is a library that helps us work with PDF files.
import json  # This library helps us work with JSON data, which is a way to store information.
import pandas as pd  # This library helps us work with tables of data.
import os  # This library helps us work with files and folders on the computer.
import pdfplumber  # This library helps us extract information from PDF files.
import streamlit as st  # This library helps us create a web app easily.
import re  # This library helps us find patterns in text.
import csv  # This library helps us work with CSV files, which are like simple tables.
from PIL import Image  # This library helps us work with images.

# Function to get information about the PDF file
def extract_metadata(doc):
    metadata = doc.metadata  # Get the information about the PDF
    num_pages = len(doc)  # Count how many pages are in the PDF
    return {"Metadata": metadata, "Total Pages": num_pages}  # Return the info as a dictionary

# Function to get all the text from the PDF
def extract_text_from_pdf(doc):
    return [page.get_text("text") for page in doc]  # Get text from each page and return it as a list

# Function to get images from the PDF
def extract_images_from_pdf(doc, output_folder="extracted_images"):
    images = []  # Create a list to store the images
    os.makedirs(output_folder, exist_ok=True)  # Make a folder to save images if it doesn't exist
    
    for page_num, page in enumerate(doc):  # Go through each page in the PDF
        for img_index, img in enumerate(page.get_images(full=True)):  # Find all images on the page
            xref = img[0]  # Get the reference number for the image
            base_image = doc.extract_image(xref)  # Extract the image using the reference number
            image_bytes = base_image["image"]  # Get the actual image data
            image_ext = base_image["ext"]  # Get the image file type (like .png or .jpg)
            image_filename = f"{output_folder}/page_{page_num+1}_img_{img_index}.{image_ext}"  # Create a name for the image file
            
            with open(image_filename, "wb") as img_file:  # Open the file to save the image
                img_file.write(image_bytes)  # Write the image data to the file
            
            images.append({"Page": page_num + 1, "Image File": image_filename})  # Add the image info to the list
    
    return images  # Return the list of images

# Function to get product details from the PDF
def extract_product_details(pdf_path, image_dir="images"):
    os.makedirs(image_dir, exist_ok=True)  # Make a folder to save product images
    doc = fitz.open(pdf_path)  # Open the PDF file
    product_data = []  # Create a list to store product information
    price_pattern = re.compile(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?")  # Create a pattern to find prices
    dimension_pattern = re.compile(r"(\d+\s*x\s*\d+\s*(?:x\s*\d+)?)")  # Create a pattern to find dimensions

    def classify_text(text):
        lines = text.split("\n")  # Split the text into lines
        current_title = None  # Variable to hold the current product title
        current_description = []  # List to hold the current product description
        current_prices = []  # List to hold the current product prices
        current_dimensions = []  # List to hold the current product dimensions

        for i, line in enumerate(lines):  # Go through each line
            line = line.strip()  # Remove extra spaces from the line
            if not line:  # If the line is empty, skip it
                continue
            
            if re.match(r"^[A-Z\s\-']+$", line):  # Check if the line is a title (all uppercase)
                if current_title and current_description:  # If we have a title and description
                    product_data.append([current_title, " ".join(current_description), ", ".join(current_prices), ", ".join(current_dimensions), ""])  # Save the product info
                current_title = lines[i-1] if i > 0 else line  # Set the current title
                current_description = []  # Reset the description
                current_prices = []  # Reset the prices
                current_dimensions = []  # Reset the dimensions
            else:
                current_description.append(line)  # Add the line to the description
                price_matches = price_pattern.findall(line)  # Find any prices in the line
                if price_matches:  # If we found prices
                    current_prices.extend(price_matches)  # Add them to the list of prices
                dimension_matches = dimension_pattern.findall(line)  # Find any dimensions in the line
                if dimension_matches:  # If we found dimensions
                    current_dimensions.extend(dimension_matches)  # Add them to the list of dimensions

        if current_title and current_description:  # If we have a title and description at the end
            product_data.append([current_title, " ".join(current_description), ", ".join(current_prices), ", ".join(current_dimensions), ""])  # Save the last product info
    
    for page_num in range(len(doc)):  # Go through each page in the PDF
        page = doc.load_page(page_num)  # Load the page
        text = page.get_text()  # Get the text from the page
        classify_text(text)  # Classify the text to find product details
        
        image_list = page.get_images(full=True)  # Get all images on the page
        max_size = 0  # Variable to keep track of the largest image size
        largest_image_filename = None  # Variable to hold the name of the largest image

        for img in image_list:  # Go through each image
            xref = img[0]  # Get the reference number for the image
            base_image = doc.extract_image(xref)  # Extract the image
            width, height = base_image.get("width", 0), base_image.get("height", 0)  # Get the width and height of the image
            size = width * height  # Calculate the size of the image
            
            if size > max_size:  # If this image is larger than the previous largest
                max_size = size  # Update the largest size
                image_bytes = base_image["image"]  # Get the image data
                largest_image_filename = f"image_{page_num}_{xref}.png"  # Create a name for the largest image
                image_path = os.path.join(image_dir, largest_image_filename)  # Create the full path for the image
                
                with open(image_path, "wb") as image_file:  # Open the file to save the image
                    image_file.write(image_bytes)  # Write the image data to the file
        
        if product_data and largest_image_filename:  # If we have product data and a largest image
            product_data[-1][-1] = largest_image_filename  # Add the image filename to the last product entry
    
    df = pd.DataFrame(product_data, columns=["Product Name", "Description", "Price", "Dimensions", "Image"])  # Create a table from the product data
    return df  # Return the table
    
# Function to get links (URLs) from the PDF
def extract_links_from_pdf(doc):
    links = []  # Create a list to store links
    
    for page_num, page in enumerate(doc):  # Go through each page
        for link in page.get_links():  # Get all links on the page
            links.append({"Page": page_num + 1, "Link": link.get("uri", "")})  # Save the page number and link
    
    return links  # Return the list of links

# Function to get tables from the PDF
def extract_tables_from_pdf(pdf_path):
    tables = []  # Create a list to store tables
    
    with pdfplumber.open(pdf_path) as pdf:  # Open the PDF with pdfplumber
        for page_num, page in enumerate(pdf.pages, start=1):  # Go through each page
            extracted_tables = page.extract_tables()  # Extract tables from the page
            for table in extracted_tables:  # Go through each table found
                tables.append({"Page": page_num, "Table": table})  # Save the table with the page number
    
    return tables  # Return the list of tables

# Streamlit UI (User  Interface)
st.title("PDF Data Extractor")  # Set the title of the web app
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])  # Create a button to upload a PDF file

if uploaded_file:  # If a file is uploaded
    pdf_path = f"temp_{uploaded_file.name}"  # Create a temporary name for the PDF file
    with open(pdf_path, "wb") as f:  # Open the file to save the uploaded PDF
        f.write(uploaded_file.getbuffer())  # Write the uploaded file data to the temporary file
    
    doc = fitz.open(pdf_path)  # Open the PDF file
    
    st.subheader("PDF Preview")  # Create a subheader for the preview section
    total_pages = len(doc)  # Count how many pages are in the PDF
    st.write(f"Total Pages: {total_pages}")  # Show the total number of pages
    
    page_num = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1, step=1)  # Create a number input to select a page

    image = doc[page_num - 1].get_pixmap()  # Get the image of the selected page
    img = Image.frombytes("RGB", [image.width, image.height], image.samples)  # Convert the image data to a format we can show
    st.image(img, caption=f"Page {page_num}", use_column_width=True)  # Show the image of the page
    
    metadata = extract_metadata(doc)  # Get the metadata of the PDF
    images = extract_images_from_pdf(doc)  # Get images from the PDF
    product_details = extract_product_details(pdf_path)  # Get product details from the PDF
    
    # Create tabs for different sections of the extracted data
    tabs = st.tabs(["Metadata","Extracted Texts", "Extracted Images", "Product Details","Extracted Links","Extracted Tables", "Log", "Save File"])
    
    with tabs[0]:  # In the Metadata tab
        st.json(metadata)  # Show the metadata in JSON format
    
    with tabs[1]:  # In the Extracted Texts tab
        st.text_area("Extracted Text", value="\n".join(extract_text_from_pdf(doc)), height=300)  # Show all extracted text

    with tabs[2]:  # In the Extracted Images tab
        img_page = st.number_input("Image Page Number", min_value=1, max_value=total_pages, value=1, step=1)  # Select a page for images
        img_files = [img_info["Image File"] for img_info in images if img_info["Page"] == img_page]  # Get images from the selected page
        for img_file in img_files:  # Show each image
            st.image(img_file, caption=f"Page {img_page}")

    with tabs[3]:  # In the Product Details tab
        st.write("Extracted Product Details")  # Show a title
        st.dataframe(product_details)  # Show the product details in a table

    with tabs[4]:  # In the Extracted Links tab
        st.json(extract_links_from_pdf(doc))  # Show extracted links in JSON format 

    with tabs[5]:  # In the Extracted Tables tab
        for table in extract_tables_from_pdf(pdf_path):  # Go through each extracted table
            df = pd.DataFrame(table["Table"])  # Convert the table to a DataFrame
            st.write(f"Page {table['Page']}")  # Show the page number
            st.dataframe(df)  # Display the table

    with tabs[6]:  # In the Log tab
        extracted_data = {"Metadata": metadata, "Images": images, "Product Details": product_details.to_dict(orient='records')}  # Prepare data for logging
        st.write(json.dumps(extracted_data, indent=4, ensure_ascii = False))
    
    with tabs[7]:  # In the Save File tab
        save_option = st.radio("Do you want to save the extracted data?", ("JSON", "CSV", "Both", "No"))  # Create radio buttons for save options
        if save_option != "No":  # If the user chooses to save the data
            filename = st.text_input("Enter filename (without extension)")  # Ask the user to enter a filename (without .json or .csv)
            if filename:  # If the user has entered a filename
                if save_option in ["JSON", "Both"]:  # If the user wants to save as JSON or both formats
                    json_file = f"{filename}.json"  # Create the JSON filename
                    with open(json_file, "w", encoding="utf-8") as f:  # Open the file to write JSON data
                        json.dump(extracted_data, f, indent=4, ensure_ascii=False)  # Save the extracted data as JSON
                    st.success(f"Data saved to {json_file}")  # Show a success message to the user
                if save_option in ["CSV", "Both"]:  # If the user wants to save as CSV or both formats
                    product_details.to_csv(f"{filename}.csv", index=False, encoding="utf-8")  # Save the product details as a CSV file
                    st.success(f"Data saved to {filename}.csv")  # Show a success message to the user
