import csv

CSV_NAME = "temp/cut_to_shape_"


class CSVWriter:
    # Data is the same format as results: A Tuple containing two Tuples
    def __init__(self, destination, data):
        print("CSV Writer Started...")
        with open(destination, 'w') as csvfile:
            docwriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
            docwriter.writerow(['Pair', 'Layer 1', 'Layer 2', 'Volume Difference', 'Unit'])

            # Add content to the CSV File.
            z = 0
            for pair, result in data.items():
                docwriter.writerow([str(z), pair[0], pair[1], result[0], result[1]])
                z += 1
        print("CSV Write Complete")
        return
