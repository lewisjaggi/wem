import argparse
import csv
import numpy as np
import os


def is_valid_file(_parser, arg):
    """
    Validate the validity of a path file.
    :param _parser: The argparse object
    :param arg: The value
    :return: Error or path file
    """
    if not os.path.exists(arg):
        _parser.error("The file %s does not exist!" % arg)
    else:
        return arg


# Creation of the argument parser for return the CSV input path file
parser = argparse.ArgumentParser(description="Convert the input CSV file in UTF-8 to an output CSV file for do the "
                                             "\"Market basket analysis\" exercise.")
parser.add_argument('PATH',
                    metavar='path_csv_file',
                    type=lambda x: is_valid_file(parser, x),
                    help='The path of the csv input file')
args = parser.parse_args()


def get_column_id(name, h):
    """
    Return the id of the column of a product
    :param name: the name of the product
    :param h: The header
    :return: The id of the column
    """
    return np.where(np.array(h) == name)[0]


def create_empty_row(customer_name, nbr_product):
    """
    Creation of an empty row (all product at False)
    :param customer_name: The name of customer
    :param nbr_product: The number of products
    :return: An array of False with the customer_name at front
    """
    array_empty = [customer_name]
    for x in range(0, nbr_product):
        array_empty.append("False")
    return np.array([array_empty])


# Reading of the csv file
data = []
with open(args.PATH, newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    header = next(reader, None)
    print("Header : [ " + " | ".join(header) + " ]")
    print(reader)
    for row in reader:
        data.append(row)
data = np.array(data)

# Keep all the column useless
interestingData = data[:, [get_column_id("Customer Name", header), get_column_id("Product Name", header)]]

# Creation list of customers and products
customers = np.unique(interestingData[:, 0])
products = np.unique(interestingData[:, 1])

# Creation of the final header of csv document.
header_out = np.concatenate([["Customer Name"], products])

# Creation of the data array of CSV out file
data_out = np.array([header_out])

# Browse the input data for build the output data
i = 0
for row in interestingData:
    i = i + 1
    customerName = str(row[0][0])
    productName = str(row[1][0])
    print(str(i) + " / " + str(len(interestingData)))

    # Check if the customer is not already in data_out and add it if it is not
    if customerName not in data_out:
        emptyRow = create_empty_row(customerName, len(products))
        data_out = np.append(data_out, emptyRow, axis=0)

    # Find the position by customer and product
    rn = np.where(data_out == customerName)[0]
    cn = np.where(header_out == productName)[0]

    # Update the cell with True
    data_out[rn[0], cn[0]] = True


# Save the data in a file in CSV format
out_filename = "ex3_data_out.csv"
np.savetxt(out_filename, data_out, delimiter="|", fmt='%s')
print("The file " + out_filename + " has been created.")
