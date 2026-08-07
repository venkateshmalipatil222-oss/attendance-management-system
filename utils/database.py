import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Venky@123",
        database="attendance_db"
    )

    return connection