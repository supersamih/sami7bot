CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS starboard (
	RootMessageID integer PRIMARY KEY,
	StarMessageID integer,
	Stars integer DEFAULT 1
);

CREATE TABLE IF NOT EXISTS quotes (
    QuoteID INTEGER PRIMARY KEY AUTOINCREMENT,
    Quote  TEXT,
    Author TEXT,
    UserID INTEGER
);

CREATE TABLE IF NOT EXISTS pokemon (
	TrainerID INTEGER,
	PokeID INTEGER,
	PokeName TEXT,
	PokeSprite TEXT,
	Legendary BOOLEAN,
	Mythical BOOLEAN
);