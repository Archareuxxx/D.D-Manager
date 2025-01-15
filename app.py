from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_FOLDER = 'db'

# Check Db Folder
if not os.path.exists(DB_FOLDER):
    os.mkdir(DB_FOLDER)

# Helper for DB connection
def get_db_connection(db_name):
    return sqlite3.connect(os.path.join(DB_FOLDER, db_name))

# Main route: Dashboard
@app.route('/')
def dashboard():
    databases = os.listdir(DB_FOLDER)
    return render_template('dashboard.html', databases=databases)

# Add database
@app.route('/add_database', methods=['POST'])
def add_database():
    db_name = request.form['db_name'] + '.db'
    path = os.path.join(DB_FOLDER, db_name)
    if os.path.exists(path):
        flash('Database already exists!', 'danger')
    else:
        conn = sqlite3.connect(path)
        conn.close()
        flash('Database added successfully!', 'success')
    return redirect(url_for('dashboard'))

# Delete database
@app.route('/delete_database/<db_name>')
def delete_database(db_name):
    path = os.path.join(DB_FOLDER, db_name)
    if os.path.exists(path):
        os.remove(path)
        flash('Database deleted successfully!', 'success')
    else:
        flash('Database not found!', 'danger')
    return redirect(url_for('dashboard'))

# Look at database table
@app.route('/view/<db_name>')
def view_tables(db_name):
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return render_template('edit_table.html', db_name=db_name, tables=tables)

# Add tabel
@app.route('/add_table/<db_name>', methods=['POST'])
def add_table(db_name):
    table_name = request.form['table_name']
    columns = request.form['columns']
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE TABLE {table_name} ({columns});")
        conn.commit()
        flash('Table added successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Error: {e}', 'danger')
    conn.close()
    return redirect(url_for('view_tables', db_name=db_name))

# Export database
@app.route('/export/<db_name>')
def export_database(db_name):
    path = os.path.join(DB_FOLDER, db_name)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
              
