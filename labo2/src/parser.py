import numpy as np
import csv

data = []


def get_column_id(name, h):
    return np.where(np.array(h) == name)[0]


def create_empty_row(customer_name, nbr_product):
    array_empty = [customer_name]
    for x in range(0, nbr_product):
        array_empty.append("False")
    return np.array([array_empty])


with open("../data/superstore_dataset2011-2015.csv", newline="") as csvFile:
    reader = csv.reader(csvFile, delimiter=',')
    header = next(reader, None)
    print("Header : [ " + " | ".join(header) + " ]")
    print(reader)
    for row in reader:
        data.append(row)
data = np.array(data)
interestingData = data[:, [get_column_id("Customer Name", header), get_column_id("Product Name", header)]]

customers = np.unique(interestingData[:, 0])
products = np.unique(interestingData[:, 1])

header_out = np.concatenate([["Customer Name"], products])

data_out = np.array([header_out])
i = 0
for row in interestingData:
    i = i + 1
    customerName = str(row[0][0])
    productName = str(row[1][0])
    print(str(i) + " / " + str(len(interestingData)))

    if customerName not in data_out:
        emptyRow = create_empty_row(customerName, len(products))
        data_out = np.append(data_out, emptyRow, axis=0)

    rn = np.where(data_out == customerName)[0]
    cn = np.where(header_out == productName)[0]
    data_out[rn[0], cn[0]] = True

np.savetxt("ex3_data_out.csv", data_out, delimiter="|", fmt='%s')
print("END")
