import sqlite3

conexion = sqlite3.connect("database.db")

with open("sql/tablas.sql","r",encoding="utf8") as archivo:
    conexion.executescript(archivo.read())

conexion.commit()
conexion.close()

print("Base creada")