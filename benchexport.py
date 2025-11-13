import csv
from datetime import datetime
import os

def export_csv(filename, datalist):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Specify the CSV file name
    csv_file_name = f"{filename}_{timestamp}.csv"
    folder = "benchmarks"
    file_path = os.path.join(folder, csv_file_name)

    # Write to CSV using csv.writer
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write data rows
        for result in datalist:
            writer.writerow(result)
