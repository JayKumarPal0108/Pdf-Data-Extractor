# README: PDF Data Extractor

## Overview

The PDF Data Extractor is a Python-based tool that extracts metadata, text, images, product details, hyperlinks, and tables from PDF documents. It uses fitz (PyMuPDF), pdfplumber, and pandas for processing and streamlit for a user-friendly interface.

# Features

Extracts Metadata: Retrieves PDF properties such as author, title, and number of pages.

Extracts Text: Extracts textual content from each page.

Extracts Images: Identifies and saves images found in the PDF.

Extracts Product Details: Detects product names, descriptions, prices, and associated images.

Extracts Hyperlinks: Retrieves URLs embedded within the PDF.

Extracts Tables: Recognizes and extracts tabular data.

Web UI: Provides an interactive user interface using Streamlit.

## Installation and Setup

Prerequisites

Ensure you have Python 3.8+ installed.

Install Dependencies

Run the following command to install required libraries:

## pip install pymupdf pandas pdfplumber streamlit

Running the Tool

Start the Streamlit application with:

## streamlit run pdf_extractor.py

This will launch the web interface where you can upload a PDF and extract data.

# How to Use This Tool

Run the Application: Start the Streamlit app using the command above.

Upload a PDF: Use the provided UI to select and upload a PDF file.

Choose Extraction Options: Select the type of data you want to extract (metadata, text, images, etc.).

View Results: Extracted data will be displayed within the UI.

Download Data: If applicable, download the extracted data in a suitable format.

## Approach

Metadata Extraction: Uses PyMuPDF (fitz) to retrieve document metadata.

Text Extraction: Reads page-wise text using PyMuPDF.

Image Extraction: Identifies and saves images to a specified directory.

Product Details Extraction: Utilizes regex to detect product names, descriptions, and prices.

Hyperlink Extraction: Retrieves embedded URLs from PDF.

Table Extraction: Uses pdfplumber to extract structured tabular data.

UI Implementation: Provides a clean and interactive UI using Streamlit.

# Assumptions and Future Improvements

## Assumptions

Product details are formatted consistently in the PDF.

Images are required for extracting relevant product information.

The tool assumes prices follow standard currency formats (e.g., $99.99).

## Potential Improvements

Improved OCR support: Integrate pytesseract for better text extraction from scanned PDFs.

Better product recognition: Implement NLP to improve text classification.

Export options: Enable data export in CSV, Excel, or JSON formats.

Performance enhancements: Optimize large PDF processing and image extraction.

Cloud storage support: Integrate cloud storage options like AWS S3 for storing extracted data.

# License

This project is open-source and can be modified for personal or commercial use.

# Gant chart 
![image](https://github.com/user-attachments/assets/d38a86e3-eb5d-4900-84c5-9f649973f200)

# ER Diagram
![image](https://github.com/user-attachments/assets/43b9aa29-81ee-436d-b910-e040290dd0fc)

# Flow Chart
![image](https://github.com/user-attachments/assets/52fd2eb3-5f5a-4e1b-8597-2787ac14476c)

