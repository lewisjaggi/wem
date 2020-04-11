import pandas as pd
import numpy as np

df_a = pd.read_csv("../data/superstore_dataset2011-2015.csv",
                   sep=",",
                   encoding="latin1",
                   header=0,
                   usecols=["Customer ID", "Product ID"])


products = df_a["Product ID"].copy().drop_duplicates()
nbr_product = products.size
print(nbr_product)
header = pd.concat([pd.Series(["Customer ID"]), products]).array
# print(header)

data_out = pd.DataFrame(columns=header).set_index("Customer ID")


all_false = ["Toto"]
for x in range(0, nbr_product):
    all_false.append("False")

print("AllFalseSize = " + str(len(all_false)))

new_row = pd.Series(all_false)
print(new_row)
data_out = pd.concat([data_out, new_row], ignore_index=True)


print(data_out)
