import mysql.connector as con
mycon = con.connect(host="sql12.freesqldatabase.com",user="sql12352288",password="7X35JENbK3",port=3306,database="sql12352288")
mycursor = mycon.cursor()
mycursor.execute("SELECT COUNT(*) FROM curie")
id = mycursor.fetchall()[0][0]