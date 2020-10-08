#!/usr/bin/env python3

import csv

borrowing_data = {}
item_key_data = {}
formcog_key_data = {}
with open("master-clean.tsv", "r") as fp:
    reader = csv.DictReader(fp, delimiter="\t")
    for row in reader:
        for numeric_key in ("mng_item", "form_set", "lgid3"):
            try:
                row[numeric_key] = int(row[numeric_key])
            except:
                pass
        if not row["borr_qual"] and not row["borr_source"]:
            continue

        strong_key = tuple((row[k] for k in ("lgid3", "mng_item", "item", "form_set", "cogn_set")))
        value = tuple((row[k] for k in ("borr_qual", "borr_source")))
        borrowing_data[strong_key] = value

        item_key = tuple((row[k] for k in ("lgid3", "mng_item", "item")))
        value = tuple((row[k] for k in ("form_set", "cogn_set")))
        item_key_data[item_key] = value

        formcog_key = tuple((row[k] for k in ("lgid3", "mng_item", "form_set", "cogn_set")))
        value = row["item"]
        formcog_key_data[formcog_key] = value


updated_rows = []
used_borrowing_keys = []
audit = []
replacements = 0
with open("Data.tsv", "r") as fp:
    reader = csv.DictReader(fp, delimiter="\t")
    for row in reader:
        for numeric_key in ("mng_item", "form_set", "lgid3"):
            try:
                row[numeric_key] = int(row[numeric_key])
            except:
                pass
        key = tuple((row[k] for k in ("lgid3", "mng_item", "item", "form_set", "cogn_set")))
        item_key = tuple((row[k] for k in ("lgid3", "mng_item", "item")))
        formcog_key = tuple((row[k] for k in ("lgid3", "mng_item", "form_set", "cogn_set")))
        replace = False
        if key in borrowing_data:
            # Strong match, just go for it
            replace = True
        elif item_key in item_key_data:
            old_form_set, old_cogn_set = item_key_data[item_key]
            while True:
                print("Weak match on item {}:".format(row["item"]))
                print("Form set: {} → {}.".format(old_form_set, row["form_set"]))
                print("Cogn set: {} → {}.".format(old_cogn_set, row["cogn_set"]))
                print("Accept? Y/N")
                decision = input().strip().lower()
                if decision in ("y", "n"):
                    break
                else:
                    print("What?")
            if decision == "y":
                replace = True
                key = list(key)
                key[3] = old_form_set
                key[4] = old_cogn_set
                key = tuple(key)
        elif formcog_key in formcog_key_data:
            old_item = formcog_key_data[formcog_key]
            while True:
                print("Weak match on form {}, cognate {}:".format(row["form_set"], row["cogn_set"]))
                print("Item: {} → {}.".format(old_item, row["item"]))
                print("Accept? Y/N")
                decision = input().strip().lower()
                if decision in ("y", "n"):
                    break
                else:
                    print("What?")
            if decision == "y":
                replace = True
                key = list(key)
                key[2] = old_item
                key = tuple(key)
        if replace:
            replacements += 1
            used_borrowing_keys.append(key)
            qual, source = borrowing_data[key]
            old_source = row["borr_source"]
            # Log non-trivials
            if not old_source or old_source not in source:
                audit.append([row.copy(), source])
            else:
                pass
            row["borr_qual"] = qual
            row["borr_source"] = source
        updated_rows.append(row)
    fieldnames = reader.fieldnames

print("Replaced {} borrowing values.".format(replacements))

with open("Data.tsv", "w") as fp:
    writer = csv.DictWriter(fp, fieldnames = fieldnames, delimiter="\t", quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for updated_row in updated_rows:
        writer.writerow(updated_row)

print("{} of these need auditing (see audit.txt)".format(len(audit)))

with open("audit.txt", "w") as fp:
    for row, new_source in audit:
        row["new_source"] = new_source
        if row["borr_source"]:
            fp.write("For language {lgid3}, meaning {mng_item}, item \"{item}\", the borrowing source changed from {borr_source} to {new_source}.\n".format(**row))
        else:
            fp.write("For language {lgid3}, meaning {mng_item}, item \"{item}\" is now identified as a borrowing from \"{new_source}\".\n".format(**row))

unused_keys = [k for k in borrowing_data.keys() if k not in used_borrowing_keys]
print("{} borrowing values could not be matched (see unused.tsv)".format(len(unused_keys)))

with open("unused.tsv", "w") as fp:
    writer = csv.writer(fp, delimiter="\t")
    fieldnames= ["lgid3", "mng_item", "item", "form_set", "cogn_set", "borr_qual", "borr_source"]
    writer.writerow(fieldnames)
    for key in unused_keys:
        row = list(key)
        row.extend(borrowing_data[key])
        writer.writerow(row)
