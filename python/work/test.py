import mysql.connector

# Step 1: Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="small_project"
)

cursor = connection.cursor()

# Step 2: Take input
first_name = input("Enter your first name: ")
last_name = input("Enter your last name: ")

# Step 3: Check if record exists
query = "SELECT international_id FROM verify WHERE first_name = %s AND last_name = %s LIMIT 1"
cursor.execute(query, (first_name, last_name))
row = cursor.fetchone()

if row:
    print("Data entered is correct.")
    international_id = row[0]  # get ID of the matched record

    # Step 4: Delete the record
    delete_query = "DELETE FROM verify WHERE international_id = %s"
    cursor.execute(delete_query, (international_id,))
    connection.commit()
    print("Record deleted successfully.")
else:
    print("Data is not correct, no record found.")

# Step 5: Close connection
cursor.close()
connection.close()
