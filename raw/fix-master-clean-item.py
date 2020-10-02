#!/usr/bin/env python3

import csv

clean_items = {}
with open("master-fixedtest.tsv", "r") as fp:
    reader = csv.DictReader(fp, delimiter="\t")
    for row in reader:
        key = tuple((row[k] for k in ("lgid3", "mng_item", "form_set", "cogn_set")))
        clean_items[key] = row["item"]

cleaned_rows = []
with open("master-clean.tsv", "r") as fp:
    reader = csv.DictReader(fp, delimiter="\t")
    for row in reader:
        key = tuple((row[k] for k in ("lgid3", "mng_item", "form_set", "cogn_set")))
        if key in clean_items:
            dirty = row["item"]
            clean = clean_items[key]
            if clean != dirty:
                print("Transforming dirty {} into clean {}.".format(dirty, clean))
                row["item"] = clean
        cleaned_rows.append(row)
    fieldnames = reader.fieldnames

with open("master-clean.tsv", "w") as fp:
    writer = csv.DictWriter(fp, fieldnames = fieldnames, delimiter="\t")
    writer.writeheader()
    for clean_row in cleaned_rows:
        writer.writerow({k:v.strip() for k,v in clean_row.items()})
