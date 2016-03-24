#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import json

def load_csv(fname, sep=','):
    f = open(fname)
    lines = f.readlines()
    f.close()
    column_names = lines[0].strip().split(sep)
    key_name = column_names[0]
    ds = {}
    for line in lines[1:]:
        values = line.strip().split(sep)
        d = {}
        for i in range(len(column_names)):
            d[column_names[i]] = values[i]
        ds[d[key_name]] = d
    return ds

def csv_to_json(file_root, sep=','):
    ds = load_csv(file_root + '.csv')
    f = open(file_root + '.json', 'w')
    json.dump(ds, f, indent=3, separators=(',', ': '))

if __name__ == '__main__':
    pass
