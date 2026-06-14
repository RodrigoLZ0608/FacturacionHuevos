import psycopg2

conexion = psycopg2.connect(
    "postgresql://facturacion_huevos_bj8i_user:dOuxZAjDrG6A1QFWmBZXrB2mQzg7O7Up@dpg-d8n5024m0tmc73dnsc50-a.oregon-postgres.render.com/facturacion_huevos_bj8i"
)

cursor = conexion.cursor()

with open("sql/tablas.sql", "r", encoding="utf8") as archivo:
    sql = archivo.read()

cursor.execute(sql)

conexion.commit()

cursor.close()
conexion.close()

print("Base creada correctamente")