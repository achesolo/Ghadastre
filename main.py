import csv
from csv import writer, reader
#
# file_path = "C:\\Users\\USER\\OneDrive\\Desktop\\TABLE COORDINATES.csv"
# HEADER = ("STATION", "NORTHING", "EASTING", "REMARKS")
# cleaned_data = []
# cleaned_row = []
#
# with open(file_path) as csv_file:
#     csv_reader = csv.reader(csv_file)
#     for row in csv_reader:
#         if row[HEADER.index("STATION")] == "" or \
#                 row[HEADER.index("NORTHING")] == "" or \
#                 row[HEADER.index("EASTING")] == "" or \
#                 row[HEADER.index("REMARKS")] == "" or \
#                 row[HEADER.index("EASTING")] == "#REF!" or \
#                 row[HEADER.index("REMARKS")] == '“' or \
#                 row[HEADER.index("REMARKS")] == "N/A":
#             pass
#
#         else:
#             for col in row:
#                 cleaned_row.append(col.strip())
#             cleaned_data.append(cleaned_row)
#             cleaned_row = []
#
#
# new_file_path = "C:\\Users\\USER\\OneDrive\\Desktop\\CLEANED TABLE COORDINATES.csv"
# new_cleaned_row = []
#
# with open(new_file_path, mode='w', newline="") as csv_file:
#     csv_writer = csv.writer(csv_file)
#
#     for line in cleaned_data:
#         remarks = line[HEADER.index("REMARKS")]
#         remarks = remarks.replace("PARCEL CORNER", "CORNER")
#         remarks = remarks.replace("PARCEL  CORNER", "CORNER")
#         remarks = remarks.replace("parcel", "CORNER")
#         remarks = remarks.replace("PARCEL CORNERS", "CORNER")
#         remarks = remarks.replace("PARCEL  CORNERS", "CORNER")
#         remarks = remarks.replace("PARCEL CONERS", "CORNER")
#         remarks = remarks.replace("CONERS", "CORNER")
#         remarks = remarks.replace("PARCEL CONER", "CORNER")
#         remarks = remarks.replace("PACEL CORNER", "CORNER")
#         remarks = remarks.replace("PARCELCORNER", "CORNER")
#         remarks = remarks.replace("PARCELCORNER “", "CORNER")
#         remarks = remarks.replace("“", "CORNER")
#         remarks = remarks.replace("CORNER CORNER", "CORNER")
#         remarks = remarks.replace("REFERENCES", "REFERENCE")
#         remarks = remarks.replace("CLOSURE", "REFERENCE")
#         new_cleaned_row.append(line[HEADER.index("EASTING")])
#         new_cleaned_row.append(line[HEADER.index("NORTHING")])
#         new_cleaned_row.append(remarks)
#
#         csv_writer.writerow(new_cleaned_row)
#         new_cleaned_row = []
#


file_path = "C:\\Users\\USER\\OneDrive\\Desktop\\CLEANED TABLE COORDINATES.csv"
HEADER = ("EASTING", "NORTHING", "REMARKS")
cleaned_data = [["parcelreferenceDEFAULT", "parcelboundaryDEFAULT"]]
cleaned_row = []
reference = "MULTIPOINT("
corner = "POLYGON(("
first_corner = ""

with open(file_path) as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if row[HEADER.index("REMARKS")] == "REFERENCE":
            if cleaned_row:
                corner += first_corner + "))"
                cleaned_row.append(corner)
                corner = "POLYGON(("
                cleaned_data.append(cleaned_row)
                cleaned_row = []
            reference += str(row[HEADER.index("EASTING")]) + " " + str(row[HEADER.index("NORTHING")]) + ", "

        if row[HEADER.index("REMARKS")] == "CORNER":
            if not cleaned_row:
                reference = reference.rstrip(", ")
                reference += ")"
                cleaned_row.append(reference)
                reference = "MULTIPOINT("
                first_corner = str(row[HEADER.index("EASTING")]) + " " + str(row[HEADER.index("NORTHING")])
            corner += str(row[HEADER.index("EASTING")]) + " " + str(row[HEADER.index("NORTHING")]) + ", "


new_file_path = "C:\\Users\\USER\\OneDrive\\Desktop\\WKT TABLE COORDINATES.csv"

with open(new_file_path, mode='w', newline="") as csv_file:
    csv_writer = csv.writer(csv_file)

    for line in cleaned_data:
        csv_writer.writerow(line)

