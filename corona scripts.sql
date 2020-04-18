--DROP TABLE IF EXISTS RawData;
CREATE TABLE IF NOT EXISTS RawData (
    id integer PRIMARY KEY AUTOINCREMENT,
    int_id integer NOT NULL,
    country text NOT NULL,
    province text NULL,
    cases text NULL,
    deaths text NULL,
    recovered text NULL
);

--DROP TABLE IF EXISTS Cases;
CREATE TABLE IF NOT EXISTS Cases (
    id integer PRIMARY KEY AUTOINCREMENT,
    int_id integer NOT NULL,
    country text NOT NULL,
    province text NULL,
    cases_day datetime NULL,
    caseNum integer NULL   
);

--DROP TABLE IF EXISTS Deaths;
CREATE TABLE IF NOT EXISTS Deaths (
    id integer PRIMARY KEY AUTOINCREMENT,
    int_id integer NOT NULL,
    country text NOT NULL,
    province text NULL,
    deaths_day datetime NULL,
    deathNum integer NULL   
);

--DROP TABLE IF EXISTS Recovered;
CREATE TABLE IF NOT EXISTS Recovered (
    id integer PRIMARY KEY AUTOINCREMENT,
    int_id integer NOT NULL,
    country text NOT NULL,
    province text NULL,
    recovered_day datetime NULL,
    recoveredNum integer NULL   
);