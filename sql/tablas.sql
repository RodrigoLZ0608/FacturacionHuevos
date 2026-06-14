CREATE TABLE Clientes(
    id SERIAL PRIMARY KEY ,
    nombre TEXT NOT NULL,
    direccion TEXT,
    distrito TEXT
);

CREATE TABLE Proveedores(
    id SERIAL PRIMARY KEY ,
    nombre TEXT NOT NULL,
    direccion TEXT,
    distrito TEXT
);

CREATE TABLE TipoHuevo(
    id SERIAL PRIMARY KEY ,
    nombre TEXT NOT NULL
);

INSERT INTO TipoHuevo(nombre) VALUES ('Comercial');
INSERT INTO TipoHuevo(nombre) VALUES ('Jumbo');
INSERT INTO TipoHuevo(nombre) VALUES ('Pardo');

--------------------------------------------------
-- COMPRAS
--------------------------------------------------

CREATE TABLE LiquidacionCompra(
    id SERIAL PRIMARY KEY ,
    fecha_compra DATE NOT NULL,
    proveedor_id INTEGER NOT NULL,
    importe_total REAL NOT NULL,

    FOREIGN KEY(proveedor_id)
    REFERENCES Proveedores(id)
);

CREATE TABLE DetalleCompra(
    id SERIAL PRIMARY KEY ,
    liquidacion_compra_id INTEGER NOT NULL,
    tipo_huevo_id INTEGER NOT NULL,
    precio_kg REAL NOT NULL,
    peso_total REAL NOT NULL,
    cantidad_paquetes INTEGER NOT NULL,
    importe REAL NOT NULL,
    columnas INTEGER,

    FOREIGN KEY(liquidacion_compra_id)
    REFERENCES LiquidacionCompra(id),

    FOREIGN KEY(tipo_huevo_id)
    REFERENCES TipoHuevo(id)
);

CREATE TABLE PesoPaqueteCompra(
    id SERIAL PRIMARY KEY ,
    detalle_compra_id INTEGER NOT NULL,
    peso REAL NOT NULL,
    posicion INTEGER,

    FOREIGN KEY(detalle_compra_id)
    REFERENCES DetalleCompra(id)
);

--------------------------------------------------
-- VENTAS
--------------------------------------------------

CREATE TABLE LiquidacionVenta(
    id SERIAL PRIMARY KEY ,
    fecha_venta DATE NOT NULL,
    cliente_id INTEGER NOT NULL,
    importe_total REAL NOT NULL,

    FOREIGN KEY(cliente_id)
    REFERENCES Clientes(id)
);

CREATE TABLE DetalleVenta(
    id SERIAL PRIMARY KEY ,
    liquidacion_venta_id INTEGER NOT NULL,
    tipo_huevo_id INTEGER NOT NULL,
    precio_kg REAL NOT NULL,
    peso_total REAL NOT NULL,
    cantidad_paquetes INTEGER NOT NULL,
    importe REAL NOT NULL,

    columnas INTEGER,

    FOREIGN KEY(liquidacion_venta_id)
    REFERENCES LiquidacionVenta(id),

    FOREIGN KEY(tipo_huevo_id)
    REFERENCES TipoHuevo(id)
);

CREATE TABLE PesoPaqueteVenta(
    id SERIAL PRIMARY KEY ,
    detalle_venta_id INTEGER NOT NULL,
    peso REAL NOT NULL,
    posicion INTEGER,

    FOREIGN KEY(detalle_venta_id)
    REFERENCES DetalleVenta(id)
);

CREATE TABLE Competidores(
    id SERIAL PRIMARY KEY ,
    nombre TEXT NOT NULL,
    direccion TEXT,
    distrito TEXT
);

CREATE TABLE IF NOT EXISTS Reportes(
    id SERIAL PRIMARY KEY ,
    fecha_reporte TEXT,

    fecha_compra TEXT,
    fecha_venta TEXT,

    inversion_total REAL,
    venta_total REAL,

    costo_flete REAL,
    flete REAL,

    ganancia_bruta REAL,
    ganancia REAL,

    porcentaje_ganancia_bruta REAL,
    porcentaje_ganancia_inversion REAL,

    diferencia_kg REAL,
    precio_promedio REAL,
    perdida REAL,

    compras_json TEXT,
    ventas_json TEXT,

    totales_compra_json TEXT,
    totales_venta_json TEXT
);