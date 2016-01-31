#!/usr/bin/python -i

import json
import random
import psycopg2

f = open('names.json')
names = json.loads(f.read())
f.close()

def name_generator(gender=['male','female'], ethnicity=['other'], n=20):
    given_names = []
    for g in gender:
        for e in ethnicity:
            given_names += names['given'][g][e]
    surnames = names['surnames']['other']

    return ("%s %s" % (
        random.choice(given_names), 
        random.choice(surnames))
            for i in range(n))


def name_list(gender=['male','female'], ethnicity=['other'], n=20):
    given_names = []
    for g in gender:
        for e in ethnicity:
            given_names += names['given'][g][e]
    surnames = names['surnames']['other']

    return ["%s %s" % (
        random.choice(given_names), 
        random.choice(surnames))
            for i in range(n)]


def init_db():

    db = psycopg2.connect('dbname=names')
    cursor = db.cursor()

    for gender in ['male', 'female']:
        for ethnicity in ['asian', 'hispanic', 'black', 'white', 'other']:
            for name in names['given'][gender][ethnicity]:
                if ethnicity == 'other':
                    ethnicity = None
                cursor.execute('''
                INSERT INTO names
                VALUES (DEFAULT, %(name)s, %(n_type)s, %(ethnicity)s)
                ''', {
                    'name': name,
                    'n_type': 'given_' + gender,
                    'ethnicity': ethnicity
                })

    for surname in names['surnames']['other']:
        cursor.execute('''
        INSERT INTO names
        VALUES (DEFAULT, %(name)s, %(n_type)s, %(ethnicity)s)
        ''', {
            'name': surname,
            'n_type': 'surname',
            'ethnicity': None
        })

    db.commit()
    db.close()

def query(qs,args=()):
    db = psycopg2.connect('dbname=names')
    cursor = db.cursor()
    cursor.execute(qs+';', args)
    result = cursor.fetchall()
    db.commit()
    db.close()
    return result


def surnames():
    names = query('select * from names where n_type = %s', ('surname',))
    return map(lambda x: x[1], names)

def male_names():
    names = query('select * from names where n_type = %s', ('given_male',))
    return map(lambda x: x[1], names)

def female_names():
    names = query('select * from names where n_type = %s', ('given_female',))
    return map(lambda x: x[1], names)


def get_names(n_types=[], e_types=[]):
    qs = 'SELECT * FROM names %s'
    qt = _where(n_types, e_types)
    print qs % qt
    return map(lambda x: x[1], query(qs % qt))

def _eq(name, _types):
    return map((lambda x: "%s='%s'" % (name,x)), _types)

def _or(term_list):
    return reduce((lambda x,y: "(%s) OR (%s)" % (x,y)), term_list)

def _and(term_list):
    return reduce((lambda x,y: "(%s) AND (%s)" % (x,y)), term_list)

def _where(n_types, e_types):
    if len(n_types) == 0:
        if len(e_types) == 0:
            return ''
        else:
            return 'WHERE %s ' % _or(_eq('ethnicity', e_types))
    else:
        if len(e_types) == 0:
            return 'WHERE %s ' % _or(_eq('n_type', n_types))
        else:
            return 'WHERE ' + _and([_or(_eq('n_type', n_types)),_or(_eq('ethnicity', e_types))])

def gen_name():
    return "%s %s" % (random.choice(first), random.choice(last))

if __name__ == '__main__':
    first = get_names(['given_male','given_female'],[])
    last = get_names(['surname'],[])
