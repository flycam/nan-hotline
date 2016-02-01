CREATE TABLE actions
(
    id INTEGER PRIMARY KEY NOT NULL,
    time TIMESTAMP NOT NULL,
    "case" INTEGER DEFAULT nextval('actions_case_seq'::regclass) NOT NULL
);
CREATE TABLE cases
(
    id INTEGER PRIMARY KEY NOT NULL,
    title VARCHAR(100),
    assigned_supporter INTEGER,
    description TEXT
);
CREATE TABLE supporter_phones
(
    id INTEGER PRIMARY KEY NOT NULL,
    supporter INTEGER DEFAULT nextval('supporter_phones_supporter_seq'::regclass) NOT NULL,
    sip_uri VARCHAR(2000) NOT NULL
);
CREATE TABLE supporters
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(200) NOT NULL,
    telegram_id INTEGER NOT NULL,
    password VARCHAR(200) NOT NULL,
    username VARCHAR(100) NOT NULL
);
CREATE TABLE wizard_calls
(
    id INTEGER DEFAULT nextval('actions_id_seq'::regclass) NOT NULL,
    time TIMESTAMP NOT NULL,
    supporter_phone INTEGER DEFAULT nextval('wizard_calls_supporter_phone_seq'::regclass) NOT NULL,
    supportee_sip_uri VARCHAR(2000) NOT NULL,
    path TEXT,
    "case" INTEGER DEFAULT nextval('actions_case_seq'::regclass) NOT NULL
);
ALTER TABLE actions ADD FOREIGN KEY ("case") REFERENCES cases (id);
ALTER TABLE cases ADD FOREIGN KEY (assigned_supporter) REFERENCES supporters(id);
ALTER TABLE supporter_phones ADD FOREIGN KEY (supporter) REFERENCES supporters(id);
ALTER TABLE wizard_calls ADD FOREIGN KEY (supporter_phone) REFERENCES supporter_phones (id);