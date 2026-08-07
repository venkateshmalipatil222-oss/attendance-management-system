from flask import Flask, render_template, request, redirect, url_for
from utils.database import get_db_connection

app = Flask(__name__)


# --------------------------------
# HOME / LOGIN PAGE
# --------------------------------

@app.route("/")
def home():
    return render_template("login.html")


# --------------------------------
# LOGIN
# --------------------------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user:

        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))

        elif user["role"] == "student":
            return redirect(url_for("student_dashboard"))

    return "Invalid username or password"


# --------------------------------
# ADMIN DASHBOARD
# --------------------------------

@app.route("/admin/dashboard")
def admin_dashboard():

    return render_template(
        "admin/admin_dashboard.html"
    )


# --------------------------------
# STUDENT DASHBOARD
# --------------------------------

@app.route("/student/dashboard")
def student_dashboard():

    return render_template(
        "student/student_dashboard.html"
    )


# --------------------------------
# VIEW STUDENTS
# --------------------------------

@app.route("/admin/students")
def manage_students():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM students ORDER BY student_id"
    )

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/students.html",
        students=students
    )


# --------------------------------
# ADD STUDENT
# --------------------------------

@app.route("/admin/students/add", methods=["GET", "POST"])
def add_student():

    # Show Add Student form
    if request.method == "GET":

        return render_template(
            "admin/add_student.html"
        )

    # Get form data
    username = request.form["username"]
    password = request.form["password"]
    usn = request.form["usn"]
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    semester = request.form["semester"]

    # Connect to database
    connection = get_db_connection()

    cursor = connection.cursor()

    # Insert login account
    cursor.execute(
        """
        INSERT INTO users
        (username, password, role)
        VALUES (%s, %s, 'student')
        """,
        (username, password)
    )

    # Get newly created user ID
    user_id = cursor.lastrowid

    # Insert student information
    cursor.execute(
        """
        INSERT INTO students
        (user_id, usn, name, email, phone, department, semester)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            usn,
            name,
            email,
            phone,
            department,
            semester
        )
    )

    # Save changes
    connection.commit()

    # Close database
    cursor.close()
    connection.close()

    # Return to student list
    return redirect(
        url_for("manage_students")
    )


# --------------------------------
# EDIT STUDENT
# --------------------------------

@app.route(
    "/admin/students/edit/<int:student_id>",
    methods=["GET", "POST"]
)
def edit_student(student_id):

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    # -----------------------------
    # GET - Show edit form
    # -----------------------------

    if request.method == "GET":

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        cursor.close()
        connection.close()

        if student is None:

            return "Student not found"

        return render_template(
            "admin/edit_student.html",
            student=student
        )

    # -----------------------------
    # POST - Update student
    # -----------------------------

    usn = request.form["usn"]
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    semester = request.form["semester"]

    cursor.execute(
        """
        UPDATE students
        SET
            usn = %s,
            name = %s,
            email = %s,
            phone = %s,
            department = %s,
            semester = %s
        WHERE student_id = %s
        """,
        (
            usn,
            name,
            email,
            phone,
            department,
            semester,
            student_id
        )
    )

    # Save changes
    connection.commit()

    # Close database
    cursor.close()
    connection.close()

    return redirect(
        url_for("manage_students")
    )


# --------------------------------
# ATTENDANCE
# --------------------------------

@app.route("/admin/attendance", methods=["GET", "POST"])
def attendance():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    # --------------------------------
    # GET ALL STUDENTS
    # --------------------------------

    cursor.execute(
        """
        SELECT *
        FROM students
        ORDER BY student_id
        """
    )

    students = cursor.fetchall()

    # --------------------------------
    # POST - SAVE ATTENDANCE
    # --------------------------------

    if request.method == "POST":

        attendance_date = request.form["attendance_date"]

        # Go through every student
        for student in students:

            student_id = student["student_id"]

            status = request.form[
                f"status_{student_id}"
            ]

            # Insert attendance
            cursor.execute(
                """
                INSERT INTO attendance
                (student_id, attendance_date, status)
                VALUES (%s, %s, %s)
                """,
                (
                    student_id,
                    attendance_date,
                    status
                )
            )

        # Save attendance
        connection.commit()

        cursor.close()
        connection.close()

        # Return to attendance page
        return redirect(
            url_for("attendance")
        )

    # --------------------------------
    # GET - SHOW ATTENDANCE PAGE
    # --------------------------------

    cursor.close()
    connection.close()

    return render_template(
        "admin/attendance.html",
        students=students
    )


# --------------------------------
# RUN APPLICATION
# --------------------------------


# --------------------------------
# MANAGE USERS
# --------------------------------

@app.route("/admin/users")
def manage_users():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, username, role
        FROM users
        ORDER BY id
        """
    )

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin/users.html",
        users=users
    )
if __name__ == "__main__":
    app.run(debug=True)