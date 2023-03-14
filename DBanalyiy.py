import sqlite3
db=sqlite3.connect('telbot.db')
sql=db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS profileTel (
    login TEXT,
    region TEXT,
    klass TEXT)""")
db.commit()
user_id="121"
user_region="europa"
user_klass="11"

#sql.execute(f"SELECT login FROM profileTel WHERE login = '{user_id}'")
#if sql.fetchone() is None:
    #sql.execute(f"INSERT INTO profileTel VALUES (?,?,?)", (user_id, user_region, user_klass))
    #db.commit()

for value in sql.execute("SELECT * FROM profileTel"):
    print(value)
#print("dad")
#qsq