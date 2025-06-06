def insert_course_sql():
    sql = """
    INSERT INTO COURSES (COURSE_NAME, TEE, HOLE, PAR, DISTANCE)
    VALUES (?, ?, ?, ?, ?)
    """
    return sql

def create_course_sql():
    sql = """
    CREATE TABLE IF NOT EXISTS COURSES 
    (COURSE_NAME TEXT, TEE TEXT, HOLE INT, PAR INT, DISTANCE INT)
    """
    return sql

def get_courses_sql():
    sql = """
    SELECT COURSE_NAME,
           TEE
      FROM COURSES
      GROUP BY COURSE_NAME, TEE
    """
    return sql

def insert_round_sql():
    sql = """
    INSERT INTO ROUNDS (COURSE_NAME, TEE, DATE, TEE_TIME, ROUND_ID, HOLES)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    return sql

def insert_club_sql():
    sql = """
    INSERT INTO CLUBS (CLUB_NAME, CLUB_TYPE, CLUB_BRAND, ACTIVE)
    VALUES (?, ?, ?, ?)
    """
    return sql

def select_clubs_sql():
    sql = """
    SELECT CLUB_NAME
      FROM CLUBS
      WHERE ACTIVE = 1
    """
    return sql


def select_rounds_sql():
    sql = """
    SELECT ROUND_ID,
           COURSE_NAME,
           TEE,
           DATE,
           TEE_TIME,
           HOLES 
      FROM ROUNDS
    """
    return sql

def select_holes_sql():
    sql = """
    SELECT HOLE,
           PAR,
           DISTANCE,
           COURSE_NAME,
           TEE
      FROM COURSES
     WHERE COURSE_NAME = ? AND TEE = ?
    """
    return sql

def insert_shot_sql():
    sql = """
    INSERT INTO SHOTS (ROUND_ID,
                       HOLE,
                       SHOT_NUMBER,
                       SHOT_TYPE,
                       DISTANCE,
                       CLUB,
                       PENALTY_STROKES,
                       MISS_TYPE,
                       PUTT_BREAK,
                       MAKE)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    return sql

def read_shots_sql():
    sql = """
    SELECT ROUND_ID,
                       HOLE,
                       SHOT_NUMBER,
                       SHOT_TYPE,
                       DISTANCE,
                       CLUB,
                       PENALTY_STROKES,
                       MISS_TYPE,
                       PUTT_BREAK,
                       MAKE
      FROM SHOTS
    """
    return sql

def read_shots_round():
    sql = """
    SELECT ROUND_ID,
                       HOLE,
                       SHOT_NUMBER,
                       SHOT_TYPE,
                       DISTANCE,
                       CLUB,
                       PENALTY_STROKES,
                       MISS_TYPE,
                       PUTT_BREAK,
                       MAKE
      FROM SHOTS
     WHERE ROUND_ID = ?
    """
    return sql

def read_expected_sql():
    sql = """
    SELECT * 
    FROM STROKES_GAINED_EXPECTED
    """
    return sql