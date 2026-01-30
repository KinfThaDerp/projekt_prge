CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    posts INTEGER,
    location TEXT,
    coords GEOMETRY(Point, 4326)
);