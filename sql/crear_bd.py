import psycopg2

conexion = psycopg2.connect(
    "postgresql://rodrigo:FsWz8sodqVNzWZL0JPXJ95qBSzHUNHi0@dpg-d8keqrsm0tmc73cju330-a.virginia-postgres.render.com/facturacion_huevos"
)

cursor = conexion.cursor()

with open("sql/tablas.sql", "r", encoding="utf8") as archivo:
    sql = archivo.read()

cursor.execute(sql)

conexion.commit()

cursor.close()
conexion.close()

print("Base creada correctamente")