import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="library",
    autocommit=True,
)
cursor = conn.cursor()

from app.widgets import MainWindow