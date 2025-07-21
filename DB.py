from sqlite3 import connect
import pyodbc

# 🔹 Connect to SQL Server (Windows Auth)
def connect_to_db(database_name='Bank'):
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=JOHN\\SQLEXPRESS;"
            f"DATABASE={database_name};"
            "Trusted_Connection=yes;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
        return conn
    except Exception as e:
        print("❌ Connection failed:", e)
        return None

# 🔹 Execute a query (INSERT, UPDATE, DELETE)
def execute_query(conn, query, params=None):
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        print("✅ Query executed successfully.")
    except Exception as e:
        print("❌ Query execution failed:", e)

# 🔹 Execute a SELECT query and fetch results
def fetch_query(conn, query, params=None):
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print("User not found: ")
        return []

def close_connection(conn):
    if conn:
        conn.close()