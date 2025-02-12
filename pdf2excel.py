import tkinter as tk
from tkinter import filedialog

from pdf2image import convert_from_path
import cv2
import pytesseract
import pandas as pd

import numpy as np

import os
import time

def select_pdf_file():
    """Opens a file dialog to select a PDF file."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF Files", "*.pdf")])
    return file_path

def extract_tables(pdf_path, output_folder="temp_images"):
    """Converts a PDF file into images and saves them in a directory."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path)
    tables = 0

    for i in range(len(images)):
        
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        images[i].save(image_path, "PNG")

        while(True):
            tables += 1
            
            im = cv2.imread(image_path)
            im = cv2.resize(im, (0, 0), fx = 0.6, fy = 0.6)

            x, y, w, h = cv2.selectROI('crop', im)
            im = im[y:y + h, x:x + w]

            cv2.destroyAllWindows()

            cv2.imwrite(os.path.join('tables', f'table_{tables}.png'), im)

            select_more = input('Select another table (Y/N): ').lower()

            if select_more == 'n' or select_more == 'N':
                break

        os.remove(image_path)

    print(f"Saved {tables} tables from PDF.")
    return tables

def extract_table_from_image(image_path):
    """Extracts structured tabular data from an image."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply threshold to enhance table structure
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Use pytesseract image_to_data to get word positions
    data = pytesseract.image_to_data(image, config="--oem 1 --psm 12", output_type=pytesseract.Output.DICT)

    rows = {}
    for i in range(len(data["text"])):
        if data["text"][i].strip():  # Ignore empty strings
            x, y, w, h, text = data["left"][i], data["top"][i], data["width"][i], data["height"][i], data["text"][i]

            row_key = y // 10  # Group text by row (adjust threshold as needed)
            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append((x, text))

    # Sort rows and columns
    structured_data = []
    for key in sorted(rows.keys()):
        row = sorted(rows[key], key=lambda x: x[0])  # Sort by X position
        structured_data.append([text for _, text in row])

    return pd.DataFrame(structured_data)

def save_tables_to_excel(tables: int, output_file="data/tables.xlsx"):
    """Extracts tables from multiple images and saves them into an Excel file."""
    writer = pd.ExcelWriter(output_file, engine="xlsxwriter")

    for table in range(tables):
        table_path = os.path.join('tables', f'table_{table + 1}.png')
        df = extract_table_from_image(table_path)

        #out_path = os.path.join('data', f'table_{table + 1}')
        df.to_excel(writer, sheet_name=f'table_{table + 1}', index=False, header=False)

    writer.close()
    print(f"Tables saved to {output_file}")

def clear_temps():
    try:
        files = os.listdir('tables')
        for file in files:
            file_path = os.path.join('tables', file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")


if __name__ == '__main__':
    pdf_path = select_pdf_file()
    
    if not pdf_path:
        print("No file selected. Exiting.")
        time.sleep(2)
        
        exit()
    
    tables = extract_tables(pdf_path)
    save_tables_to_excel(tables)
    clear_temps()