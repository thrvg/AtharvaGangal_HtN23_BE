from flask import Flask, request
import sqlite3
import json
import sys

app = Flask(__name__)


# Function to get user data
def get_all_user_data(user_id=-1):
    con = sqlite3.connect("hacker.db")
    cur = con.cursor()
    res = []
    all_hacker_data = None

    # If user_id = -1, return data of all users, else return data of specified id
    if user_id == -1:
        select_hackers = "SELECT * FROM hackers;"
        all_hacker_data = cur.execute(select_hackers)
    else: 
        select_hackers = "SELECT * FROM hackers WHERE id=?;"
        all_hacker_data = cur.execute(select_hackers, (user_id,))

    # Deconstruct query, and reconstruct response dictionary
    select_hacker_skills = "SELECT s.skill, hs.rating FROM hacker_skill_map hs INNER JOIN skills s ON s.id = hs.skill_id WHERE hs.hacker_id=?;"
    for hacker in all_hacker_data.fetchall():
        temp = {}
        temp_skills_arr = []
        temp["id"] = hacker[0]
        temp["name"] = hacker[1]
        temp["company"] = hacker[2]
        temp["email"] = hacker[3]
        temp["phone"] = hacker[4]
        for skill in cur.execute(select_hacker_skills, (hacker[0],)).fetchall():
            temp_skill = {}
            temp_skill["skill"] = skill[0]
            temp_skill["rating"] = skill[1]
            temp_skills_arr.append(temp_skill)
        temp["skills"] = temp_skills_arr
        res.append(temp)

    con.close()
    return res


# Function to update field specified with 'key'
def update_field(key="", new_val="", user_id=-1):

    # Assertion to check key valid
    assert key in {"name", "phone", "email", "company"}

    update_stmt = f"UPDATE hackers SET {key}=? where id=?"
    con = sqlite3.connect("hacker.db")
    cur = con.cursor()
    cur.execute(update_stmt, (new_val, user_id))
    con.commit()
    con.close()

    return

# Function to update skill list
def update_skill(skill="", new_rating="", user_id=-1):
    update_stmt = "UPDATE hacker_skill_map SET rating = ? WHERE skill_id=? AND hacker_id=?"
    skill_check = "SELECT id FROM skills WHERE skill=?"
    skill_map_check = "SELECT id FROM hacker_skill_map WHERE skill_id=? AND hacker_id=?"
    skill_insert = "INSERT INTO skills (skill) VALUES (?)"
    hacker_skill_insert = "INSERT INTO hacker_skill_map (hacker_id, skill_id, rating) VALUES (?, ?, ?)"
    con = sqlite3.connect("hacker.db")
    cur = con.cursor()

    # If skill does not exist in database, create a new skill
    record = cur.execute(skill_check, (skill,)).fetchone()
    if record is None:
        skill_id = cur.execute(skill_insert, (skill,)).lastrowid
        cur.execute(hacker_skill_insert, (user_id, skill_id, new_rating))
    else:
        # If skill exists, insert/update based on whether hacker already has skill
        skill_id = record[0]
        if cur.execute(skill_map_check, (skill_id, user_id)).fetchone() is None:
            cur.execute(hacker_skill_insert, (user_id, skill_id, new_rating))
        else:
            cur.execute(update_stmt, (new_rating, skill_id, user_id))

    con.commit()
    con.close()
    return

# Function to query and get aggregated skills
def get_aggregate(query, fil=None):
    con = sqlite3.connect("hacker.db")
    cur = con.cursor()
    res = []

    # Execute query (with or without filter), construct response
    db_set = cur.execute(query) if fil is None else cur.execute(query, fil)
    for arr in db_set.fetchall():
        temp = {}
        temp["skill"] = arr[0]
        temp["frequency"] = arr[1]
        res.append(temp)
    con.close()

    return res

# Route that returns data of all users
@app.route("/users/", methods=["GET"])
def get_all_users():
    return get_all_user_data()

# Variable route that returns data of specified user
@app.route("/users/<user_id>", methods=["GET"])
def get_selected_user(user_id):
    user_id = int(user_id)
    return get_all_user_data(user_id)
  
  
# Route that updates data of a user   
@app.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    user_id = int(user_id)

    # Update skills, and other fields in different ways due to different structures
    for key, new_val in request.get_json().items():
        if key != "id" and key != "skills":
            update_field(key, new_val, user_id)
    if "skills" in request.get_json():
        for skill in request.get_json()["skills"]:
            update_skill(skill["skill"], skill["rating"], user_id)
    return get_all_user_data(user_id)
    
# Route that returns aggregated skills
@app.route("/skills/", methods=["GET"])
def aggregate_skills():
    args = request.args
    
    # Decide to return filtered or unfiltered data
    if "max_frequency" in args and "min_frequency" in args:  
        agg_query = """
        SELECT s.skill, COUNT(hs.hacker_id) as c FROM hacker_skill_map hs 
        LEFT JOIN skills s
        ON s.id = hs.skill_id
        GROUP BY s.skill
        HAVING c BETWEEN ? AND ?
        """
        return get_aggregate(agg_query, fil=(int(args["min_frequency"]), int(args["max_frequency"])))
    else:
        agg_query = """
        SELECT s.skill, COUNT(hs.hacker_id) as c FROM hacker_skill_map hs 
        LEFT JOIN skills s
        ON s.id = hs.skill_id
        GROUP BY s.skill
        """
        return get_aggregate(agg_query)

