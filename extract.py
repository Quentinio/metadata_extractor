import os
import csv
from PIL import Image
from PIL.ExifTags import TAGS
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def extract_metadata(image_path):
    """Extract metadata, including dimensions and EXIF, from an image."""
    metadata = {}
    try:
        with Image.open(image_path) as img:
            # Get image dimensions in pixels
            width_pixels = img.width
            height_pixels = img.height
            metadata['Width (Pixels)'] = width_pixels
            metadata['Height (Pixels)'] = height_pixels
            
            # Get EXIF metadata for resolution (DPI)
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == "XResolution":
                        metadata['XResolution'] = value
                    if tag_name == "YResolution":
                        metadata['YResolution'] = value

            # Fallback resolution if EXIF DPI is not available
            x_resolution = metadata.get('XResolution', 72)
            y_resolution = metadata.get('YResolution', 72)

            # Convert pixels to millimeters using DPI
            width_mm = int(round((width_pixels / float(x_resolution)) * 25.4)) 
            height_mm = int(round((height_pixels / float(y_resolution)) * 25.4))
            metadata['Width (mm)'] = round(width_mm, 2)
            metadata['Height (mm)'] = round(height_mm, 2)

            # Determine orientation
            metadata['Orientation'] = "Landscape" if width_pixels > height_pixels else "Portrait"

            # Add file name
            metadata['File Name'] = os.path.basename(image_path)

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    return metadata

def process_folder(folder_path, output_csv):
    """Process all image files in the folder and save metadata to a CSV."""
    supported_formats = (".jpg", ".jpeg", ".png", ".tiff", ".bmp")
    metadata_list = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(supported_formats):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                metadata = extract_metadata(file_path)
                
                if metadata:  # Only add metadata if processing was successful
                    # Filter metadata to include only the required keys
                    filtered_metadata = {
                        'File Name': metadata.get('File Name', 'Unknown'),
                        'Orientation': metadata.get('Orientation', 'Unknown'),
                        'Width (mm)': metadata.get('Width (mm)', 'Unknown'),
                        'Height (mm)': metadata.get('Height (mm)', 'Unknown'),
                    }
                    metadata_list.append(filtered_metadata)

    # Sort metadata by file name
    metadata_list = sorted(metadata_list, key=lambda x: x['File Name'])

    # Write metadata to CSV
    if metadata_list:
        fieldnames = ['File Name', 'Orientation', 'Width (mm)', 'Height (mm)']  # Only required fields
        with open(output_csv, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metadata_list)
        messagebox.showinfo("Success", f"Metadata saved to {output_csv}")
    else:
        messagebox.showerror("Error", "No image files found.")

def select_folder_and_process():
    """GUI to select folder and process images."""
    folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
    if folder_path:
        output_csv = os.path.join(folder_path, "ImageMetadata.csv")
        process_folder(folder_path, output_csv)
    else:
        messagebox.showwarning("Warning", "No folder selected.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Metadata Extractor")
    root.geometry("300x150")

    label = tk.Label(root, text="Select a folder to extract image metadata:")
    label.pack(pady=10)

    button = tk.Button(root, text="Select Folder", command=select_folder_and_process)
    button.pack(pady=20)

    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()