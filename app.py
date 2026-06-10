from flask import Flask, render_template, request
from flask import jsonify
from flask import request
from flask import redirect
from flask import session
from datetime import datetime
import json
import sqlite3

app = Flask(__name__)
app.secret_key = "facturacion_huevos"

# =====================================
# PAGINA PRINCIPAL
# =====================================

@app.route("/")
def inicio():
    return render_template("index.html")


# =====================================
# CLIENTES
# =====================================


@app.route("/clientes", methods=["GET", "POST"])
def clientes():

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        distrito = request.form["distrito"]

        cursor.execute("""
        INSERT INTO Clientes
        (nombre, direccion, distrito)
        VALUES (?, ?, ?)
        """, (nombre, direccion, distrito))

        conexion.commit()
        conexion.close()

        return redirect("/clientes")


    cursor.execute("""
    SELECT *
    FROM Clientes
    ORDER BY id DESC
    """)

    lista_clientes = cursor.fetchall()

    conexion.close()

    return render_template(
        "clientes.html",
        clientes=lista_clientes
    )





# =====================================
# PROVEEDORES
# =====================================

@app.route("/proveedores", methods=["GET", "POST"])
def proveedores():

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        distrito = request.form["distrito"]

        cursor.execute("""
        INSERT INTO Proveedores
        (nombre, direccion, distrito)
        VALUES (?, ?, ?)
        """, (nombre, direccion, distrito))

        conexion.commit()
        conexion.close()

        return redirect("/proveedores")


    cursor.execute("""
    SELECT *
    FROM Proveedores
    ORDER BY id DESC
    """)

    lista_proveedores = cursor.fetchall()

    conexion.close()

    return render_template(
        "proveedores.html",
        proveedores=lista_proveedores
    )


@app.route("/eliminar_proveedor/<int:id>")
def eliminar_proveedor(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    DELETE FROM Proveedores
    WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect("/proveedores")


@app.route("/editar_proveedor/<int:id>", methods=["GET", "POST"])
def editar_proveedor(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        distrito = request.form["distrito"]

        cursor.execute("""
        UPDATE Proveedores
        SET nombre = ?,
            direccion = ?,
            distrito = ?
        WHERE id = ?
        """,
        (
            nombre,
            direccion,
            distrito,
            id
        ))

        conexion.commit()
        conexion.close()

        return redirect("/proveedores")


    cursor.execute("""
    SELECT *
    FROM Proveedores
    WHERE id = ?
    """, (id,))

    proveedor = cursor.fetchone()

    conexion.close()

    return render_template(
        "editar_proveedor.html",
        proveedor=proveedor
    )




# =====================================
# COMPRAS
# =====================================

@app.route("/compras")
def compras():

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT nombre
    FROM Proveedores
    ORDER BY nombre
    """)

    proveedores = cursor.fetchall()

    conexion.close()

    return render_template(
        "compras.html",
        proveedores=proveedores
    )




@app.route("/guardar_liquidacion", methods=["POST"])
def guardar_liquidacion():

    datos = request.get_json()

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    # Buscar proveedor

    cursor.execute("""
    SELECT id
    FROM Proveedores
    WHERE nombre = ?
    """, (datos["proveedor"],))

    fila = cursor.fetchone()

    if fila is None:

        conexion.close()

        return jsonify({
            "mensaje":"Proveedor no encontrado"
        })

    proveedor_id = fila[0]

    # Crear liquidación

    cursor.execute("""
    INSERT INTO LiquidacionCompra
    (
        fecha_compra,
        proveedor_id,
        importe_total
    )
    VALUES (?, ?, ?)
    """,
    (
        datos["fecha"],
        proveedor_id,
        datos["importe_total"]
    ))

    liquidacion_id = cursor.lastrowid

    # Detalles

    for detalle in datos["detalles"]:

        cursor.execute("""
        SELECT id
        FROM TipoHuevo
        WHERE nombre = ?
        """, (detalle["tipo_huevo"],))

        tipo_huevo_id = cursor.fetchone()[0]

        cursor.execute("""
        INSERT INTO DetalleCompra
        (
            liquidacion_compra_id,
            tipo_huevo_id,
            precio_kg,
            peso_total,
            cantidad_paquetes,
            importe
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            liquidacion_id,
            tipo_huevo_id,
            detalle["precio_kg"],
            detalle["peso_total"],
            detalle["cantidad_paquetes"],
            detalle["importe"]
        ))

        detalle_id = cursor.lastrowid

        for peso in detalle["pesos"]:

            cursor.execute("""
            INSERT INTO PesoPaqueteCompra
            (
                detalle_compra_id,
                peso
            )
            VALUES (?, ?)
            """,
            (
                detalle_id,
                peso
            ))

    conexion.commit()
    conexion.close()

    return jsonify({
        "mensaje":"Liquidación guardada correctamente"
    })

@app.route("/historial_liquidaciones")
def historial_liquidaciones():

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        LiquidacionCompra.id,
        LiquidacionCompra.fecha_compra,
        Proveedores.nombre,
        LiquidacionCompra.importe_total

    FROM LiquidacionCompra

    INNER JOIN Proveedores
    ON LiquidacionCompra.proveedor_id = Proveedores.id

    ORDER BY LiquidacionCompra.id DESC
    """)

    liquidaciones = cursor.fetchall()

    conexion.close()

    return render_template(
        "historial_liquidaciones.html",
        liquidaciones=liquidaciones
    )

@app.route("/ver_liquidacion/<int:id>")
def ver_liquidacion(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        LiquidacionCompra.fecha_compra,
        Proveedores.nombre,
        LiquidacionCompra.importe_total
    FROM LiquidacionCompra
    INNER JOIN Proveedores
        ON LiquidacionCompra.proveedor_id = Proveedores.id
    WHERE LiquidacionCompra.id = ?
    """, (id,))

    cabecera = cursor.fetchone()

    cursor.execute("""
    SELECT
        DetalleCompra.id,
        TipoHuevo.nombre,
        DetalleCompra.precio_kg,
        DetalleCompra.peso_total,
        DetalleCompra.cantidad_paquetes,
        DetalleCompra.importe

    FROM DetalleCompra

    INNER JOIN TipoHuevo
        ON DetalleCompra.tipo_huevo_id = TipoHuevo.id

    WHERE DetalleCompra.liquidacion_compra_id = ?
    """, (id,))

    detalles = cursor.fetchall()

    detalles_completos = []

    for d in detalles:

        detalle_id = d[0]

        cursor.execute("""
        SELECT peso
        FROM PesoPaqueteCompra
        WHERE detalle_compra_id = ?
        """, (detalle_id,))

        pesos = cursor.fetchall()

        lista_pesos = [p[0] for p in pesos]

        tabla = []

        for fila in range(20):

            fila_actual = []

            for columna in range(6):

                indice = columna * 20 + fila

                if indice < len(lista_pesos):
                    fila_actual.append(lista_pesos[indice])
                else:
                    fila_actual.append("")

            tabla.append(fila_actual)

        detalles_completos.append({

            "tipo_huevo": d[1],
            "precio_kg": d[2],
            "peso_total": d[3],
            "cantidad_paquetes": d[4],
            "importe": d[5],
            "tabla": tabla

        })

    conexion.close()

    return render_template(
        "ver_liquidacion.html",
        cabecera=cabecera,
        detalles=detalles_completos
    )

# =====================================
# VENTAS
# =====================================

@app.route("/ventas")
def ventas():

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT nombre
    FROM Clientes
    ORDER BY nombre
    """)

    clientes = cursor.fetchall()

    conexion.close()

    return render_template(
        "ventas.html",
        clientes=clientes
    )

@app.route("/guardar_venta", methods=["POST"])
def guardar_venta():

    datos = request.get_json()

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    # Buscar cliente
    cursor.execute("""
    SELECT id
    FROM Clientes
    WHERE nombre = ?
    """, (datos["cliente"],))

    fila = cursor.fetchone()

    if fila is None:
        conexion.close()
        return jsonify({"mensaje": "Cliente no encontrado"})

    cliente_id = fila[0]

    # Crear liquidación venta
    cursor.execute("""
    INSERT INTO LiquidacionVenta
    (
        fecha_venta,
        cliente_id,
        importe_total
    )
    VALUES (?, ?, ?)
    """,
    (
        datos["fecha"],
        cliente_id,
        datos["importe_total"]
    ))

    liquidacion_id = cursor.lastrowid

    # Detalles
    for detalle in datos["detalles"]:

        cursor.execute("""
        SELECT id
        FROM TipoHuevo
        WHERE nombre = ?
        """, (detalle["tipo_huevo"],))

        tipo_huevo_id = cursor.fetchone()[0]

        cursor.execute("""
        INSERT INTO DetalleVenta
        (
            liquidacion_venta_id,
            tipo_huevo_id,
            precio_kg,
            peso_total,
            cantidad_paquetes,
            importe
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            liquidacion_id,
            tipo_huevo_id,
            detalle["precio_kg"],
            detalle["peso_total"],
            detalle["cantidad_paquetes"],
            detalle["importe"]
        ))

        detalle_id = cursor.lastrowid

        for peso in detalle["pesos"]:

            cursor.execute("""
            INSERT INTO PesoPaqueteVenta
            (
                detalle_venta_id,
                peso
            )
            VALUES (?, ?)
            """,
            (
                detalle_id,
                peso
            ))

    conexion.commit()
    conexion.close()

    return jsonify({
        "mensaje": "Venta guardada correctamente"
    })

@app.route("/historial_ventas")
def historial_ventas():

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        LiquidacionVenta.id,
        LiquidacionVenta.fecha_venta,
        Clientes.nombre,
        LiquidacionVenta.importe_total

    FROM LiquidacionVenta

    INNER JOIN Clientes
    ON LiquidacionVenta.cliente_id = Clientes.id

    ORDER BY LiquidacionVenta.id DESC
    """)

    ventas = cursor.fetchall()

    conexion.close()

    return render_template(
        "historial_ventas.html",
        ventas=ventas
    )

@app.route("/ver_venta/<int:id>")
def ver_venta(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        LiquidacionVenta.fecha_venta,
        Clientes.nombre,
        LiquidacionVenta.importe_total
    FROM LiquidacionVenta
    INNER JOIN Clientes
        ON LiquidacionVenta.cliente_id = Clientes.id
    WHERE LiquidacionVenta.id = ?
    """, (id,))

    cabecera = cursor.fetchone()

    cursor.execute("""
    SELECT
        DetalleVenta.id,
        TipoHuevo.nombre,
        DetalleVenta.precio_kg,
        DetalleVenta.peso_total,
        DetalleVenta.cantidad_paquetes,
        DetalleVenta.importe

    FROM DetalleVenta

    INNER JOIN TipoHuevo
        ON DetalleVenta.tipo_huevo_id = TipoHuevo.id

    WHERE DetalleVenta.liquidacion_venta_id = ?
    """, (id,))

    detalles = cursor.fetchall()

    detalles_completos = []

    for d in detalles:

        detalle_id = d[0]

        cursor.execute("""
        SELECT peso
        FROM PesoPaqueteVenta
        WHERE detalle_venta_id = ?
        """, (detalle_id,))

        pesos = cursor.fetchall()

        lista_pesos = [p[0] for p in pesos]

        tabla = []

        for fila in range(20):
            fila_actual = []

            for columna in range(6):
                indice = columna * 20 + fila

                if indice < len(lista_pesos):
                    fila_actual.append(lista_pesos[indice])
                else:
                    fila_actual.append("")

            tabla.append(fila_actual)

        detalles_completos.append({
            "tipo_huevo": d[1],
            "precio_kg": d[2],
            "peso_total": d[3],
            "cantidad_paquetes": d[4],
            "importe": d[5],
            "tabla": tabla
        })

    conexion.close()

    return render_template(
        "ver_venta.html",
        cabecera=cabecera,
        detalles=detalles_completos
    )

@app.route("/eliminar_venta/<int:id>")
def eliminar_venta(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id
    FROM DetalleVenta
    WHERE liquidacion_venta_id = ?
    """, (id,))

    detalles = cursor.fetchall()

    for d in detalles:

        cursor.execute("""
        DELETE FROM PesoPaqueteVenta
        WHERE detalle_venta_id = ?
        """, (d[0],))

    cursor.execute("""
    DELETE FROM DetalleVenta
    WHERE liquidacion_venta_id = ?
    """, (id,))

    cursor.execute("""
    DELETE FROM LiquidacionVenta
    WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect("/historial_ventas")


# =====================================
# REPORTES
# =====================================

@app.route("/reportes", methods=["GET", "POST"])
def reportes():
        if request.method == "GET":
            session.pop("fecha_compra", None)
            session.pop("fecha_venta", None)

            return render_template(
                "reportes.html",

                proveedores={},
                clientes={},

                # Compras
                peso_comercial=0,
                importe_comercial=0,
                paquetes_comercial=0,

                peso_pardo=0,
                importe_pardo=0,
                paquetes_pardo=0,

                peso_jumbo=0,
                importe_jumbo=0,
                paquetes_jumbo=0,

                peso_total_dia=0,
                importe_total_dia=0,
                paquetes_total_dia=0,

                # Ventas
                peso_comercial_venta=0,
                importe_comercial_venta=0,
                paquetes_comercial_venta=0,

                peso_pardo_venta=0,
                importe_pardo_venta=0,
                paquetes_pardo_venta=0,

                peso_jumbo_venta=0,
                importe_jumbo_venta=0,
                paquetes_jumbo_venta=0,

                peso_total_venta=0,
                importe_total_venta=0,
                paquetes_total_venta=0,

                # Resumen económico
                costo_flete=1.4,

                ganancia_bruta=0,
                ganancia=0,
                flete=0,

                porcentaje_ganancia_bruta=0,
                porcentaje_ganancia_inversion=0,

                porcentaje_flete_ganancia_bruta=0,
                porcentaje_flete_compras=0,

                porcentaje_ganancia_ganancia_bruta=0,

                diferencia_kg=0,
                precio_promedio=0,
                perdida=0
            )

        accion = request.form.get("accion", "")
        
        accion_actual = accion
        # Costo del flete por paquete
        costo_flete = float(
            request.form.get(
                "costo_flete",
                session.get("costo_flete", 1.4)
            )
        )
        session["costo_flete"] = costo_flete
        fecha_compra = session.get("fecha_compra")
        fecha_venta = session.get("fecha_venta")

        if request.form.get("fecha_compra"):
            session["fecha_compra"] = request.form["fecha_compra"]
            fecha_compra = session["fecha_compra"]

        if request.form.get("fecha_venta"):
            session["fecha_venta"] = request.form["fecha_venta"]
            fecha_venta = session["fecha_venta"]

        if accion == "compras":
            session["fecha_compra"] = request.form.get("fecha_compra")
            fecha_compra = session.get("fecha_compra")

        if accion == "ventas":
            session["fecha_venta"] = request.form.get("fecha_venta")
            fecha_venta = session.get("fecha_venta")


        TIPOS = ["Comercial", "Pardo", "Jumbo"]


        def estructura_base():
            return {
                tipo: {
                    "peso": 0,
                    "precio": 0,
                    "importe": 0,
                    "paquetes": 0
                }
                for tipo in TIPOS
            }


        def procesar_filas(filas):

            datos = {}

            for fila in filas:

                nombre = fila[0]
                tipo = fila[1]

                peso = fila[2] or 0
                precio = fila[3] or 0
                importe = fila[4] or 0
                paquetes = fila[5] or 0

                if nombre not in datos:
                    datos[nombre] = estructura_base()

                if tipo not in datos[nombre]:
                    datos[nombre][tipo] = {
                        "peso": 0,
                        "precio": 0,
                        "importe": 0,
                        "paquetes": 0
                    }

                datos[nombre][tipo]["peso"] += peso
                datos[nombre][tipo]["importe"] += importe
                datos[nombre][tipo]["paquetes"] += paquetes
                datos[nombre][tipo]["precio"] = precio

            for nombre, info in datos.items():

                info["peso_total"] = sum(
                    info[t]["peso"]
                    for t in info
                    if isinstance(info[t], dict)
                )

                info["importe_total"] = sum(
                    info[t]["importe"]
                    for t in info
                    if isinstance(info[t], dict)
                )

                info["paquetes_total"] = sum(
                    info[t]["paquetes"]
                    for t in info
                    if isinstance(info[t], dict)
                )

            return datos


        def calcular_totales(datos):

            resultado = {}

            for tipo in TIPOS:

                resultado[f"peso_{tipo.lower()}"] = sum(
                    x[tipo]["peso"]
                    for x in datos.values()
                )

                resultado[f"importe_{tipo.lower()}"] = sum(
                    x[tipo]["importe"]
                    for x in datos.values()
                )

                resultado[f"paquetes_{tipo.lower()}"] = sum(
                    x[tipo]["paquetes"]
                    for x in datos.values()
                )

            resultado["peso_total"] = sum(
                resultado[f"peso_{t.lower()}"]
                for t in TIPOS
            )

            resultado["importe_total"] = sum(
                resultado[f"importe_{t.lower()}"]
                for t in TIPOS
            )

            resultado["paquetes_total"] = sum(
                resultado[f"paquetes_{t.lower()}"]
                for t in TIPOS
            )

            return resultado


        datos_proveedores = {}
        datos_clientes = {}

        totales_compra = {
            "peso_comercial": 0,
            "importe_comercial": 0,
            "paquetes_comercial": 0,

            "peso_pardo": 0,
            "importe_pardo": 0,
            "paquetes_pardo": 0,

            "peso_jumbo": 0,
            "importe_jumbo": 0,
            "paquetes_jumbo": 0,

            "peso_total": 0,
            "importe_total": 0,
            "paquetes_total": 0
        }

        totales_venta = {
            "peso_comercial": 0,
            "importe_comercial": 0,
            "paquetes_comercial": 0,

            "peso_pardo": 0,
            "importe_pardo": 0,
            "paquetes_pardo": 0,

            "peso_jumbo": 0,
            "importe_jumbo": 0,
            "paquetes_jumbo": 0,

            "peso_total": 0,
            "importe_total": 0,
            "paquetes_total": 0
        }


        with sqlite3.connect("database.db") as conexion:
            cursor = conexion.cursor()

            

            # =========================
            # COMPRAS
            # =========================
            if fecha_compra:

                cursor.execute("""
                    SELECT
                        Proveedores.nombre,
                        TipoHuevo.nombre,
                        DetalleCompra.peso_total,
                        DetalleCompra.precio_kg,
                        DetalleCompra.importe,
                        DetalleCompra.cantidad_paquetes
                    FROM LiquidacionCompra
                    INNER JOIN Proveedores
                        ON LiquidacionCompra.proveedor_id = Proveedores.id
                    INNER JOIN DetalleCompra
                        ON LiquidacionCompra.id = DetalleCompra.liquidacion_compra_id
                    INNER JOIN TipoHuevo
                        ON DetalleCompra.tipo_huevo_id = TipoHuevo.id
                    WHERE LiquidacionCompra.fecha_compra = ?
                    ORDER BY Proveedores.nombre
                """, (fecha_compra,))

                datos_proveedores = procesar_filas(
                    cursor.fetchall()
                )

                totales_compra = calcular_totales(
                    datos_proveedores
                )

            # =========================
            # VENTAS
            # =========================
            if fecha_venta:

                cursor.execute("""
                    SELECT
                        Clientes.nombre,
                        TipoHuevo.nombre,
                        DetalleVenta.peso_total,
                        DetalleVenta.precio_kg,
                        DetalleVenta.importe,
                        DetalleVenta.cantidad_paquetes
                    FROM LiquidacionVenta
                    INNER JOIN Clientes
                        ON LiquidacionVenta.cliente_id = Clientes.id
                    INNER JOIN DetalleVenta
                        ON LiquidacionVenta.id = DetalleVenta.liquidacion_venta_id
                    INNER JOIN TipoHuevo
                        ON DetalleVenta.tipo_huevo_id = TipoHuevo.id
                    WHERE LiquidacionVenta.fecha_venta = ?
                    ORDER BY Clientes.nombre
                """, (fecha_venta,))

                datos_clientes = procesar_filas(
                    cursor.fetchall()
                )

                totales_venta = calcular_totales(
                    datos_clientes
                )

            
        
        # ======================================
        # RESUMEN ECONÓMICO
        # ======================================


        importe_total_compras = totales_compra["importe_total"]
        importe_total_ventas = totales_venta["importe_total"]

        peso_total_compras = totales_compra["peso_total"]
        peso_total_ventas = totales_venta["peso_total"]

        paquetes_total_compras = totales_compra["paquetes_total"]

        # Ganancia bruta
        ganancia_bruta = (
            importe_total_ventas
            - importe_total_compras
        )

        # Flete
        flete = (
            paquetes_total_compras
            * costo_flete
        )

        # Ganancia
        ganancia = ganancia_bruta - flete

        # Porcentajes
        porcentaje_ganancia_bruta = (
            (ganancia_bruta / importe_total_compras) * 100
            if importe_total_compras > 0 else 0
        )

        porcentaje_ganancia_inversion = (
            (ganancia / importe_total_compras) * 100
            if importe_total_compras > 0 else 0
        )

        porcentaje_flete_ganancia_bruta = (
            (flete / ganancia_bruta) * 100
            if ganancia_bruta != 0 else 0
        )

        porcentaje_flete_compras = (
            (flete / importe_total_compras) * 100
            if importe_total_compras > 0 else 0
        )

        porcentaje_ganancia_ganancia_bruta = (
            (ganancia / ganancia_bruta) * 100
            if ganancia_bruta != 0 else 0
        )

        # Diferencia de kilos
        diferencia_kg = (
            peso_total_compras
            - peso_total_ventas
        )

        # Precio promedio
        precio_promedio = (
            importe_total_compras / peso_total_compras
            if peso_total_compras > 0 else 0
        )

        # Pérdida
        perdida = diferencia_kg * precio_promedio

        if accion == "guardar_reporte":

            compras_json = json.dumps(datos_proveedores)
            ventas_json = json.dumps(datos_clientes)

            totales_compra_json = json.dumps(totales_compra)
            totales_venta_json = json.dumps(totales_venta)

            fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with sqlite3.connect("database.db") as conexion:
                cursor = conexion.cursor()

                cursor.execute("""
                INSERT INTO Reportes(
                    fecha_reporte,
                    fecha_compra,
                    fecha_venta,
                    inversion_total,
                    venta_total,
                    costo_flete,
                    flete,
                    ganancia_bruta,
                    ganancia,
                    porcentaje_ganancia_bruta,
                    porcentaje_ganancia_inversion,
                    diferencia_kg,
                    precio_promedio,
                    perdida,
                    compras_json,
                    ventas_json,
                    totales_compra_json,
                    totales_venta_json
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                fecha_reporte,
                fecha_compra,
                fecha_venta,
                importe_total_compras,
                importe_total_ventas,
                costo_flete,
                flete,
                ganancia_bruta,
                ganancia,
                porcentaje_ganancia_bruta,
                porcentaje_ganancia_inversion,
                diferencia_kg,
                precio_promedio,
                perdida,
                compras_json,
                ventas_json,
                totales_compra_json,
                totales_venta_json
            ))

                conexion.commit()

        return render_template(
            "reportes.html",
            fecha_compra=fecha_compra,
            fecha_venta=fecha_venta,

            accion_actual=accion_actual,

            proveedores=datos_proveedores,
            clientes=datos_clientes,

            # Compras
            peso_comercial=totales_compra["peso_comercial"],
            importe_comercial=totales_compra["importe_comercial"],
            paquetes_comercial=totales_compra["paquetes_comercial"],

            peso_pardo=totales_compra["peso_pardo"],
            importe_pardo=totales_compra["importe_pardo"],
            paquetes_pardo=totales_compra["paquetes_pardo"],

            peso_jumbo=totales_compra["peso_jumbo"],
            importe_jumbo=totales_compra["importe_jumbo"],
            paquetes_jumbo=totales_compra["paquetes_jumbo"],

            peso_total_dia=totales_compra["peso_total"],
            importe_total_dia=totales_compra["importe_total"],
            paquetes_total_dia=totales_compra["paquetes_total"],

            # Ventas
            peso_comercial_venta=totales_venta["peso_comercial"],
            importe_comercial_venta=totales_venta["importe_comercial"],
            paquetes_comercial_venta=totales_venta["paquetes_comercial"],

            peso_pardo_venta=totales_venta["peso_pardo"],
            importe_pardo_venta=totales_venta["importe_pardo"],
            paquetes_pardo_venta=totales_venta["paquetes_pardo"],

            peso_jumbo_venta=totales_venta["peso_jumbo"],
            importe_jumbo_venta=totales_venta["importe_jumbo"],
            paquetes_jumbo_venta=totales_venta["paquetes_jumbo"],

            peso_total_venta=totales_venta["peso_total"],
            importe_total_venta=totales_venta["importe_total"],
            paquetes_total_venta=totales_venta["paquetes_total"],

            costo_flete=costo_flete,

            ganancia_bruta=ganancia_bruta,
            ganancia=ganancia,
            flete=flete,

            porcentaje_ganancia_bruta=porcentaje_ganancia_bruta,
            porcentaje_ganancia_inversion=porcentaje_ganancia_inversion,

            porcentaje_flete_ganancia_bruta=porcentaje_flete_ganancia_bruta,
            porcentaje_flete_compras=porcentaje_flete_compras,

            porcentaje_ganancia_ganancia_bruta=porcentaje_ganancia_ganancia_bruta,

            diferencia_kg=diferencia_kg,
            precio_promedio=precio_promedio,
            perdida=perdida

    
        )



@app.route("/historial_reportes")
def historial_reportes():

    with sqlite3.connect("database.db") as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id,
                fecha_reporte,
                inversion_total,
                venta_total,
                ganancia
            FROM Reportes
            ORDER BY id DESC
        """)

        reportes = cursor.fetchall()

    return render_template(
        "historial_reportes.html",
        reportes=reportes
    )


@app.route("/eliminar_reporte/<int:id>")
def eliminar_reporte(id):

    with sqlite3.connect("database.db") as conexion:

        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM Reportes WHERE id=?",
            (id,)
        )

        conexion.commit()

    return redirect("/historial_reportes")

@app.route("/ver_reporte/<int:id>")
def ver_reporte(id):


    with sqlite3.connect("database.db") as conexion:

        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM Reportes WHERE id=?",
            (id,)
        )

        reporte = cursor.fetchone()


        if reporte is None:
            return "Reporte no encontrado"

        compras = json.loads(reporte[15]) if reporte[15] else {}
        ventas = json.loads(reporte[16]) if reporte[16] else {}

        totales_compra = json.loads(reporte[17]) if reporte[17] else {}
        totales_venta = json.loads(reporte[18]) if reporte[18] else {}

    return render_template(
        "ver_reporte.html",
        reporte=reporte,
        compras=compras,
        ventas=ventas,
        totales_compra=totales_compra,
        totales_venta=totales_venta
    )

@app.route("/eliminar_liquidacion/<int:id>")
def eliminar_liquidacion(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id
    FROM DetalleCompra
    WHERE liquidacion_compra_id = ?
    """, (id,))

    detalles = cursor.fetchall()

    for d in detalles:

        cursor.execute("""
        DELETE FROM PesoPaqueteCompra
        WHERE detalle_compra_id = ?
        """, (d[0],))

    cursor.execute("""
    DELETE FROM DetalleCompra
    WHERE liquidacion_compra_id = ?
    """, (id,))

    cursor.execute("""
    DELETE FROM LiquidacionCompra
    WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect("/historial_liquidaciones")


@app.route("/eliminar_cliente/<int:id>")
def eliminar_cliente(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    DELETE FROM Clientes
    WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect("/clientes")


@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        distrito = request.form["distrito"]

        cursor.execute("""
        UPDATE Clientes
        SET nombre = ?,
            direccion = ?,
            distrito = ?
        WHERE id = ?
        """,
        (
            nombre,
            direccion,
            distrito,
            id
        ))

        conexion.commit()
        conexion.close()

        return redirect("/clientes")


    cursor.execute("""
    SELECT *
    FROM Clientes
    WHERE id = ?
    """,(id,))

    cliente = cursor.fetchone()

    conexion.close()

    return render_template(
        "editar_cliente.html",
        cliente=cliente
    )

@app.route("/competidores", methods=["GET", "POST"])
def competidores():

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        distrito = request.form["distrito"]

        cursor.execute("""
        INSERT INTO Competidores
        (nombre, direccion, distrito)
        VALUES (?, ?, ?)
        """, (nombre, direccion, distrito))

        conexion.commit()
        conexion.close()

        return redirect("/competidores")


    cursor.execute("""
    SELECT *
    FROM Competidores
    ORDER BY id DESC
    """)

    lista_competidores = cursor.fetchall()

    conexion.close()

    return render_template(
        "competidores.html",
        competidores=lista_competidores
    )


@app.route("/eliminar_competidor/<int:id>")
def eliminar_competidor(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    cursor.execute("""
    DELETE FROM Competidores
    WHERE id = ?
    """, (id,))

    conexion.commit()
    conexion.close()

    return redirect("/competidores")


@app.route("/editar_competidor/<int:id>", methods=["GET", "POST"])
def editar_competidor(id):

    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        distrito = request.form["distrito"]

        cursor.execute("""
        UPDATE Competidores
        SET nombre = ?,
            direccion = ?,
            distrito = ?
        WHERE id = ?
        """,
        (
            nombre,
            direccion,
            distrito,
            id
        ))

        conexion.commit()
        conexion.close()

        return redirect("/competidores")


    cursor.execute("""
    SELECT *
    FROM Competidores
    WHERE id = ?
    """,(id,))

    competidor = cursor.fetchone()

    conexion.close()

    return render_template(
        "editar_competidor.html",
        competidor=competidor
    )

@app.route("/historial_precios", methods=["GET","POST"])
def historial_precios():

    periodo = "dia"
    if request.method == "POST":
        periodo = request.form["periodo"]

    if periodo == "dia":

        campo_fecha = "LiquidacionCompra.fecha_compra"
        campo_fecha_venta = "LiquidacionVenta.fecha_venta"

    elif periodo == "semana":

        campo_fecha = "strftime('%Y-%W', LiquidacionCompra.fecha_compra)"
        campo_fecha_venta = "strftime('%Y-%W', LiquidacionVenta.fecha_venta)"

    elif periodo == "mes":

        campo_fecha = "strftime('%Y-%m', LiquidacionCompra.fecha_compra)"
        campo_fecha_venta = "strftime('%Y-%m', LiquidacionVenta.fecha_venta)"

    else:

        campo_fecha = "strftime('%Y', LiquidacionCompra.fecha_compra)"
        campo_fecha_venta = "strftime('%Y', LiquidacionVenta.fecha_venta)"

    with sqlite3.connect("database.db") as conexion:

        cursor = conexion.cursor()

        # COMPRAS
        cursor.execute(f"""
        SELECT
            {campo_fecha},
            TipoHuevo.nombre,
            AVG(DetalleCompra.precio_kg)

        FROM DetalleCompra

        INNER JOIN LiquidacionCompra
        ON DetalleCompra.liquidacion_compra_id=LiquidacionCompra.id

        INNER JOIN TipoHuevo
        ON TipoHuevo.id=DetalleCompra.tipo_huevo_id

        GROUP BY
            {campo_fecha},
            TipoHuevo.nombre

        ORDER BY
            {campo_fecha}

        """)

        compras = cursor.fetchall()


        # VENTAS
        cursor.execute(f"""
            SELECT
                {campo_fecha_venta},
                TipoHuevo.nombre,
                AVG(DetalleVenta.precio_kg)

            FROM DetalleVenta

            INNER JOIN LiquidacionVenta
                ON DetalleVenta.liquidacion_venta_id = LiquidacionVenta.id

            INNER JOIN TipoHuevo
                ON DetalleVenta.tipo_huevo_id = TipoHuevo.id

            GROUP BY
                {campo_fecha_venta},
                TipoHuevo.nombre

            ORDER BY
                {campo_fecha_venta}
        """)

        ventas = cursor.fetchall()

    # =========================
    # DATOS PARA GRAFICO COMPRAS
    # =========================

    fechas = []

    precios_comercial = []
    precios_pardo = []
    precios_jumbo = []

    for fila in compras:

        fecha = fila[0]
        tipo = fila[1]
        precio = fila[2]

        if fecha not in fechas:
            fechas.append(fecha)

        if tipo == "Comercial":
            precios_comercial.append(precio)

        elif tipo == "Pardo":
            precios_pardo.append(precio)

        elif tipo == "Jumbo":
            precios_jumbo.append(precio)

    # =========================
    # DATOS PARA GRAFICO VENTAS
    # =========================

    fechas_venta = []
    precios_comercial_venta = []
    precios_pardo_venta = []
    precios_jumbo_venta = []

    for fila in ventas:

        fecha = fila[0]
        tipo = fila[1]
        precio = fila[2]

        if fecha not in fechas_venta:
            fechas_venta.append(fecha)

        if tipo == "Comercial":
            precios_comercial_venta.append(precio)

        elif tipo == "Pardo":
            precios_pardo_venta.append(precio)

        elif tipo == "Jumbo":
            precios_jumbo_venta.append(precio)


    return render_template(
        "historial_precios.html",

        compras=compras,
        ventas=ventas,
        periodo=periodo,

        fechas=fechas,
        precios_comercial=precios_comercial,
        precios_pardo=precios_pardo,
        precios_jumbo=precios_jumbo,

        fechas_venta=fechas_venta,
        precios_comercial_venta=precios_comercial_venta,
        precios_pardo_venta=precios_pardo_venta,
        precios_jumbo_venta=precios_jumbo_venta
)



# =====================================
# EJECUTAR
# =====================================

if __name__ == "__main__":
    app.run(debug=True)