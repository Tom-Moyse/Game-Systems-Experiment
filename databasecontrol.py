import sqlite3
from hashlib import sha256
from time import time


class databaseController:
    """Class used for interfacing with game database"""
    def __init__(self):
        # Connection to db established and cursor object instantiated
        self._connection = sqlite3.connect("MyGame.db")
        self._cursor = self._connection.cursor()
        self._loginPlayerID = None

    def _hash_pass(self, password):
        return sha256(password.encode()).hexdigest()

    def _check_user_exists(self, username):
        SQL = "SELECT playerID FROM tblPlayers WHERE playerUsername = ?"
        result = self._cursor.execute(SQL, [username]).fetchone()
        return result is not None

    def check_login(self):
        if self._loginPlayerID is None:
            return False
        else:
            return True

    def login(self, username, password):
        SQL = "SELECT playerID FROM tblPlayers WHERE playerUsername = ? AND playerPassword = ?"
        result = self._cursor.execute(SQL, [username, self._hash_pass(password)]).fetchone()
        if result is None:
            return False
        else:
            self._loginPlayerID = result[0]
            return True


    def get_all_scores_sc_desc(self,page):
        SQL = """
        SELECT tblPlayers.playerUsername, tblScores.score, DATE(tblDates.date, 'unixepoch')
        FROM tblScores
        INNER JOIN tblDates ON tblDates.dateID = tblScores.dateID
        INNER JOIN tblPlayers ON tblPlayers.playerID = tblScores.playerID
        ORDER BY score DESC
        LIMIT {},{}
        """.format(page*10, 10)

        return self._cursor.execute(SQL).fetchall()

    def get_all_scores_dt_desc(self,page):
        SQL = """
        SELECT tblPlayers.playerUsername, tblScores.score, DATE(tblDates.date, 'unixepoch')
        FROM tblScores
        INNER JOIN tblDates ON tblDates.dateID = tblScores.dateID
        INNER JOIN tblPlayers ON tblPlayers.playerID = tblScores.playerID
        ORDER BY date DESC
        LIMIT {},{}
        """.format(page*10, 10)

        return self._cursor.execute(SQL).fetchall()

    def get_all_users(self):
        SQL = """
        SELECT * FROM tblPlayers
        ORDER BY playerUsername DESC
        LIMIT 10
        """

        return self._cursor.execute(SQL).fetchall()

    def add_score(self, score):
        self._cursor.execute("INSERT INTO tblDates (date) VALUES (strftime('%s','now'))")
        idnum = self._cursor.execute("SELECT MAX(dateID) FROM tblDates").fetchone()[0]
        SQL = "INSERT INTO tblScores (score, dateID, playerID) VALUES (?, ?, ?)"
        self._cursor.execute(SQL, [score, idnum, self._loginPlayerID])
        self._connection.commit()

    def add_user(self, uname, password):
        if not self._check_user_exists(uname):
            SQL = "INSERT INTO tblPlayers (playerUsername, playerPassword) VALUES (?, ?)"
            self._cursor.execute(SQL, [uname, self._hash_pass(password)])
        else:
            print("Username already taken")
            return False
        self._connection.commit()
        return True

    def close_connection(self):
        self._connection.close()
        del(self)



if __name__ == "__main__":
    dbc = databaseController()
    for row in dbc.get_all_users():
        print(row)

    dbc.close_connection()
