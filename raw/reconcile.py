#!/usr/bin/env python3

import csv

def populate_dict(dictionary, filename):
    with open(filename, "r") as fp:
        reader = csv.DictReader(fp, delimiter="\t")
        for row in reader:
            if not row["borr_source"]:
                continue
            key = (row["borr_source"], row["borr_qual"])
            value = (row["lgid3"], row["mng_item"])
            if key not in dictionary:
                dictionary[key] = set()
            dictionary[key].add(value)

goal_values = {}
populate_dict(goal_values, "master-clean.tsv")
current_values = {}
populate_dict(current_values, "Data.tsv")

for key, goal in goal_values.items():
    current = current_values.get(key, set())
    if goal == current:
        continue
    elif len(goal) > len(current):
        print("master-clean.tsv contains {} more instances of {} than Data.tsv".format(len(goal) - len(current), key))
        for x in goal - current:
            print("\tlgid3 {}, mng_item {} is missing from Data.tsv".format(*x))
    else:
        print("Data.tsv contains {} instances of {} which are not in master-clean.tsv".format(len(current) - len(goal), key))
        for x in current - goal:
            print("\tlgid3 {}, mng_item {} is only in Data.tsv".format(*x))
