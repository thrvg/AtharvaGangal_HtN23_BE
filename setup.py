import sqlite3
import json

# Open db connection and initialize cursor
con = sqlite3.connect("hacker.db")
cur = con.cursor()


create_hackers_table = """
CREATE TABLE IF NOT EXISTS hackers
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name   VARCHAR(50) NOT NULL,
        company VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL,
        phone VARCHAR(50) NOT NULL
    )
"""
cur.execute(create_hackers_table)

create_skills_table = """
CREATE TABLE IF NOT EXISTS skills
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill   VARCHAR(50) NOT NULL
    )
"""
cur.execute(create_skills_table)

create_hackers_skills_table = """
CREATE TABLE IF NOT EXISTS hacker_skill_map
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hacker_id INTEGER NOT NULL,
        skill_id  INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        FOREIGN KEY (hacker_id) REFERENCES hackers(id),
        FOREIGN KEY (skill_id) REFERENCES skills(id)
    )
"""
cur.execute(create_hackers_skills_table)
            
# Use local data
f = open('data.json')
data = json.load(f)

hacker_insert = "INSERT INTO hackers (name, company, email, phone) VALUES (?, ?, ?, ?)"
skill_insert = "INSERT INTO skills (skill) VALUES (?)"
hacker_skill_insert = "INSERT INTO hacker_skill_map (hacker_id, skill_id, rating) VALUES (?, ?, ?)"
skill_check = "SELECT id FROM skills WHERE skill=?"

for d in data:

    # Insert new hacker
    hacker_id = cur.execute(hacker_insert, (d["name"], d["company"], d["email"], d["phone"])).lastrowid

    for s in d["skills"]:
        # Check if skill already in database, if not, create new skill
        record = cur.execute(skill_check, (s["skill"],)).fetchone()
        if record is None:
            skill_id = cur.execute(skill_insert, (s["skill"],)).lastrowid
        else:
            skill_id = record[0]
        
        # With the hacker_id and returned skill_id, map each hacker to each skill
        cur.execute(hacker_skill_insert, (hacker_id, skill_id, s["rating"]))

# Commit changes (for update/insert)
con.commit()

# Close db connection
con.close()