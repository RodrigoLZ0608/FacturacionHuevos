import psycopg2

conexion = psycopg2.connect(
    "postgresql://facturacion_huevos_db_user:JaTMhAvnpiKQN4mYFwQqL8si6BhSv772@dpg-dboda9c9v7es73eurgig-a.oregon-postgres.render.com/facturacion_huevos_db"
)

cursor = conexion.cursor()

with open("sql/tablas.sql", "r", encoding="utf8") as archivo:
    sql = archivo.read()

cursor.execute(sql)

conexion.commit()

cursor.close()
conexion.close()

print("Base creada correctamente")