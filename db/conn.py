import pymysql.cursors

try:
    connection = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'supply_db_test',
    port = 3306,
    cursorclass = pymysql.cursors.DictCursor
)
except:
    print('---------ERROR DB---------')
else:
    print('---------CONNECTION ESTABLISHED---------')