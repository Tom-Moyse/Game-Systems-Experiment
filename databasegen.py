import sqlite3

connection = sqlite3.connect("MyGame.db")
cursor = connection.cursor()

cursor.execute("""DROP TABLE tblPlayers""")
cursor.execute("""DROP TABLE tblScores""")
cursor.execute("""DROP TABLE tblDates""")

cursor.execute("""
CREATE TABLE tblPlayers
(
playerID INTEGER PRIMARY KEY AUTOINCREMENT,
playerUsername TEXT,
playerPassword INTEGER
)
""")

cursor.execute("""
CREATE TABLE tblDates
(
dateID INTEGER PRIMARY KEY AUTOINCREMENT,
date INTEGER
)
""")

cursor.execute("""
CREATE TABLE tblScores
(
scoreID INTEGER PRIMARY KEY AUTOINCREMENT,
score INTEGER,
dateID INTEGER,
playerID INTEGER,
FOREIGN KEY (dateID) REFERENCES tblDates(dateID)
FOREIGN KEY (playerID) REFERENCES tblPlayers(playerID)
)
""")

connection.commit()

connection.close()