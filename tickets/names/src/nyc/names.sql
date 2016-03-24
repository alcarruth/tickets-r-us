

DROP DATABASE IF EXISTS names;
CREATE DATABASE names;
\c names

CREATE TYPE name_type AS ENUM ('given_male', 'given_female', 'surname');
CREATE TYPE ethnicity_type AS ENUM ('asian', 'hispanic', 'black', 'white', 'other');

CREATE TABLE names (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    n_type name_type not null,
    ethnicity ethnicity_type
    );

