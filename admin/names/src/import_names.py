#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

def load_csv(fname, sep=','):
    f = open(fname)
    lines = f.readlines()
    f.close()
    keys = lines[0].strip().split(sep)
    ds = {}
    for line in lines[1:]:
        values = line.strip().split(sep)
        d = {}
        for i in range(len(keys)):
            key = keys[i]
            if key == 'Name':
                d[key] = values[i].capitalize()
                name = d[key]
            else:
                d[key] = values[i]
        ds[name] = d
    return ds

def csv_to_json(file_root, sep=','):
    ds = load_csv(file_root + '.csv')
    f = open(file_root + '.json', 'w')
    json.dump(ds, f, indent=3, separators=(',', ': '))

if __name__ == '__main__':
    for file_root in  ['female_names', 'male_names', 'surnames']:
        csv_to_json(file_root)

