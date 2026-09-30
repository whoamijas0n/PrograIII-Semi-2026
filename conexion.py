import os
import sqlite3

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception


class Conexion:
    _instancia = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia is None:
            cls._instancia = super(Conexion, cls).__new__(cls)
            cls._instancia._iniciado = False
        return cls._instancia

    def __init__(self):
        if getattr(self, '_iniciado', False):
            return
        self._iniciado = True

        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "db_sistema_impuestos"
        self.db_type = None
        self.conexion = None

        if MYSQL_AVAILABLE:
            try:
                conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=False
                )
                if conn.is_connected():
                    self.conexion = conn
                    self.db_type = "mysql"
                    print("Conexion exitosa a MySQL")
            except Exception as e:
                print(f"MySQL no disponible o no accesible ({e}). Iniciando motor SQLite...")

        if not self.conexion:
            self._conectar_sqlite()

    def _conectar_sqlite(self):
        self.db_type = "sqlite"
        db_path = os.path.join(os.path.dirname(__file__), "db_sistema_impuestos.sqlite")
        debe_inicializar = not os.path.exists(db_path)
        self.conexion = sqlite3.connect(db_path, check_same_thread=False)
        self.conexion.row_factory = sqlite3.Row
        print(f"Conexion exitosa a base de datos SQLite ({db_path})")
        if debe_inicializar:
            self._inicializar_schema_sqlite()

    def _formatear_sql(self, sql):
        if self.db_type == "sqlite":
            return sql.replace("%s", "?")
        return sql

    def _inicializar_schema_sqlite(self):
        cursor = self.conexion.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
              idCliente INTEGER PRIMARY KEY AUTOINCREMENT,
              codigo TEXT NOT NULL,
              nombre TEXT NOT NULL,
              direccion TEXT NOT NULL,
              telefono TEXT NOT NULL,
              email TEXT NOT NULL,
              tipo TEXT NOT NULL DEFAULT 'particular'
            );

            INSERT OR IGNORE INTO clientes (idCliente, codigo, nombre, direccion, telefono, email, tipo) VALUES
            (1, '001', 'Luis Hernandez', 'Usulutan', '4545-3256', 'luishernandez@ugb.edu.sv', 'particular'),
            (2, '002', 'Empresa Comercial San Salvador S.A. de C.V.', 'San Salvador', '2225-8900', 'contacto@comercialsansalvador.com', 'empresa');

            CREATE TABLE IF NOT EXISTS productos (
              idProducto INTEGER PRIMARY KEY AUTOINCREMENT,
              codigo TEXT NOT NULL UNIQUE,
              nombre TEXT NOT NULL,
              tipo TEXT NOT NULL DEFAULT 'impuesto',
              precio_general NUMERIC NOT NULL DEFAULT 0.0000
            );

            INSERT OR IGNORE INTO productos (idProducto, codigo, nombre, tipo, precio_general) VALUES
            (1, '11801', 'Impuesto a las Actividades Económicas Comercio', 'impuesto', 0.0000),
            (2, '11802', 'Impuesto a las Actividades Económicas Industria', 'impuesto', 0.0000);

            CREATE TABLE IF NOT EXISTS tarifas (
              idTarifa INTEGER PRIMARY KEY AUTOINCREMENT,
              idProducto INTEGER NOT NULL,
              desde NUMERIC NOT NULL,
              hasta NUMERIC NOT NULL,
              precio_base NUMERIC NOT NULL,
              adicional NUMERIC NOT NULL DEFAULT 0.0000,
              porcentaje NUMERIC NOT NULL DEFAULT 0.00,
              fecha_vigencia_desde TEXT NOT NULL,
              fecha_vigencia_hasta TEXT DEFAULT NULL,
              version TEXT NOT NULL DEFAULT 'v1',
              activa INTEGER NOT NULL DEFAULT 1,
              FOREIGN KEY (idProducto) REFERENCES productos(idProducto)
            );

            -- Tarifas Comercio (11801) - Sección 8 (Vacío entre 6000.01 y 8000.00)
            INSERT OR IGNORE INTO tarifas (idTarifa, idProducto, desde, hasta, precio_base, adicional, porcentaje, fecha_vigencia_desde, version, activa) VALUES
            (1, 1, 0.01, 500.00, 1.50, 0.00, 0.00, '2022-01-01', 'v1', 1),
            (2, 1, 500.01, 1000.00, 1.50, 3.00, 0.00, '2022-01-01', 'v1', 1),
            (3, 1, 1000.01, 2000.00, 3.00, 3.00, 0.00, '2022-01-01', 'v1', 1),
            (4, 1, 2000.01, 3000.00, 6.00, 3.00, 0.00, '2022-01-01', 'v1', 1),
            (5, 1, 3000.01, 6000.00, 9.00, 2.00, 0.00, '2022-01-01', 'v1', 1),
            (6, 1, 8000.01, 18000.00, 15.00, 2.00, 0.00, '2022-01-01', 'v1', 1),
            (7, 1, 18000.01, 30000.00, 39.00, 2.00, 0.00, '2022-01-01', 'v1', 1),
            (8, 1, 30000.01, 60000.00, 63.00, 1.00, 0.00, '2022-01-01', 'v1', 1),
            (9, 1, 60000.01, 100000.00, 93.00, 0.80, 0.00, '2022-01-01', 'v1', 1),
            (10, 1, 100000.01, 200000.00, 125.00, 0.70, 0.00, '2022-01-01', 'v1', 1),
            (11, 1, 200000.01, 300000.00, 195.00, 0.60, 0.00, '2022-01-01', 'v1', 1),
            (12, 1, 300000.01, 400000.00, 255.00, 0.45, 0.00, '2022-01-01', 'v1', 1),
            (13, 1, 400000.01, 500000.00, 300.00, 0.40, 0.00, '2022-01-01', 'v1', 1),
            (14, 1, 500000.01, 1000000.00, 340.00, 0.30, 0.00, '2022-01-01', 'v1', 1),
            (15, 1, 1000000.01, 99999999.99, 490.00, 0.18, 0.00, '2022-01-01', 'v1', 1),
            -- Tarifas Industria (11802)
            (16, 2, 0.01, 500.00, 1.50, 0.00, 0.00, '2022-01-01', 'v1', 1),
            (17, 2, 500.01, 1000.00, 1.50, 3.00, 0.00, '2022-01-01', 'v1', 1),
            (18, 2, 1000.01, 2000.00, 3.00, 3.00, 0.00, '2022-01-01', 'v1', 1),
            (19, 2, 2000.01, 3000.00, 6.00, 3.00, 0.00, '2022-01-01', 'v1', 1),
            (20, 2, 3000.01, 6000.00, 9.00, 2.00, 0.00, '2022-01-01', 'v1', 1),
            (21, 2, 8000.01, 18000.00, 15.00, 2.00, 0.00, '2022-01-01', 'v1', 1),
            (22, 2, 18000.01, 30000.00, 39.00, 2.00, 0.00, '2022-01-01', 'v1', 1),
            (23, 2, 30000.01, 60000.00, 63.00, 1.00, 0.00, '2022-01-01', 'v1', 1),
            (24, 2, 60000.01, 100000.00, 93.00, 0.80, 0.00, '2022-01-01', 'v1', 1),
            (25, 2, 100000.01, 200000.00, 125.00, 0.70, 0.00, '2022-01-01', 'v1', 1),
            (26, 2, 200000.01, 300000.00, 195.00, 0.60, 0.00, '2022-01-01', 'v1', 1),
            (27, 2, 300000.01, 400000.00, 255.00, 0.45, 0.00, '2022-01-01', 'v1', 1),
            (28, 2, 400000.01, 500000.00, 300.00, 0.40, 0.00, '2022-01-01', 'v1', 1),
            (29, 2, 500000.01, 1000000.00, 340.00, 0.30, 0.00, '2022-01-01', 'v1', 1),
            (30, 2, 1000000.01, 99999999.99, 490.00, 0.18, 0.00, '2022-01-01', 'v1', 1);

            CREATE TABLE IF NOT EXISTS periodos_actividades_economicas (
              idPeriodo INTEGER PRIMARY KEY AUTOINCREMENT,
              idCliente INTEGER NOT NULL,
              idProducto INTEGER NOT NULL,
              idTarifa INTEGER DEFAULT NULL,
              fecha_desde TEXT NOT NULL,
              fecha_hasta TEXT NOT NULL,
              balance NUMERIC NOT NULL,
              cantidad NUMERIC NOT NULL DEFAULT 1.00,
              precio_mensual NUMERIC NOT NULL,
              subtotal NUMERIC NOT NULL,
              version_formula TEXT NOT NULL DEFAULT 'BLOQUES_CEIL_2026',
              formula_detalle TEXT DEFAULT NULL,
              estado TEXT NOT NULL DEFAULT 'vigente',
              facturado INTEGER NOT NULL DEFAULT 0,
              fecha_calculo TEXT NOT NULL,
              usuario_creacion TEXT NOT NULL DEFAULT 'admin',
              fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              usuario_modificacion TEXT DEFAULT NULL,
              fecha_modificacion TEXT DEFAULT NULL,
              FOREIGN KEY (idCliente) REFERENCES clientes(idCliente),
              FOREIGN KEY (idProducto) REFERENCES productos(idProducto)
            );

            -- Semilla de períodos históricos de ejemplo (Sección 7)
            -- 2022: 700.00 -> $2.10
            -- 2023: 545.00 -> $4.50
            -- 2024: 550.00 -> $4.50
            -- 2025: 550.00 -> $4.50
            -- 2026: 550.00 -> $4.50
            -- Suma visual de precios: 2.10 + 4.50 + 4.50 + 4.50 + 4.50 = 20.10
            INSERT OR IGNORE INTO periodos_actividades_economicas 
            (idPeriodo, idCliente, idProducto, idTarifa, fecha_desde, fecha_hasta, balance, cantidad, precio_mensual, subtotal, version_formula, formula_detalle, estado, facturado, fecha_calculo) VALUES
            (1, 2, 1, 2, '2022-01-01', '2023-01-01', 700.00, 1.00, 2.100000, 2.10, 'PROPORCIONAL_HISTORICA', 'Fórmula histórica: 1.50 + ((700.00 - 500.00) / 1000 * 3.00) = $2.10', 'historico', 1, '2022-01-01 10:00:00'),
            (2, 2, 1, 2, '2023-01-01', '2024-01-01', 545.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'historico', 1, '2023-01-01 10:00:00'),
            (3, 2, 1, 2, '2024-01-01', '2025-01-01', 550.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'historico', 1, '2024-01-01 10:00:00'),
            (4, 2, 1, 2, '2025-01-01', '2026-01-01', 550.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'historico', 0, '2025-01-01 10:00:00'),
            (5, 2, 1, 2, '2026-01-01', '2027-01-01', 550.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'vigente', 0, '2026-01-01 10:00:00');

            CREATE TABLE IF NOT EXISTS bitacora_auditoria (
              idAuditoria INTEGER PRIMARY KEY AUTOINCREMENT,
              idPeriodo INTEGER NOT NULL,
              accion TEXT NOT NULL,
              balance_anterior NUMERIC DEFAULT NULL,
              balance_nuevo NUMERIC DEFAULT NULL,
              precio_anterior NUMERIC DEFAULT NULL,
              precio_nuevo NUMERIC DEFAULT NULL,
              motivo TEXT DEFAULT NULL,
              usuario_autoriza TEXT DEFAULT NULL,
              fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS recibos (
              idRecibo INTEGER PRIMARY KEY AUTOINCREMENT,
              idCliente INTEGER NOT NULL,
              fecha_emision TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              periodo_cobro_desde TEXT NOT NULL,
              periodo_cobro_hasta TEXT NOT NULL,
              total NUMERIC NOT NULL
            );

            CREATE TABLE IF NOT EXISTS detalles_recibo (
              idDetalle INTEGER PRIMARY KEY AUTOINCREMENT,
              idRecibo INTEGER NOT NULL,
              idPeriodo INTEGER NOT NULL,
              idProducto INTEGER NOT NULL,
              meses_aplicables INTEGER NOT NULL DEFAULT 1,
              precio_mensual NUMERIC NOT NULL,
              subtotal NUMERIC NOT NULL,
              FOREIGN KEY (idRecibo) REFERENCES recibos(idRecibo),
              FOREIGN KEY (idPeriodo) REFERENCES periodos_actividades_economicas(idPeriodo)
            );
        """)
        self.conexion.commit()

    def consultar(self, sql, datos=None):
        try:
            sql_conv = self._formatear_sql(sql)
            if self.db_type == "mysql":
                cursor = self.conexion.cursor(dictionary=True)
            else:
                cursor = self.conexion.cursor()

            if datos:
                cursor.execute(sql_conv, tuple(datos) if isinstance(datos, (list, tuple)) else datos)
            else:
                cursor.execute(sql_conv)

            filas = cursor.fetchall()
            if self.db_type == "sqlite":
                return [dict(f) for f in filas]
            return filas
        except Exception as e:
            print(f"Error al consultar la base de datos: {e}")
            return None

    def ejecutar(self, sql, datos=None):
        try:
            sql_conv = self._formatear_sql(sql)
            cursor = self.conexion.cursor()
            if datos:
                cursor.execute(sql_conv, tuple(datos) if isinstance(datos, (list, tuple)) else datos)
            else:
                cursor.execute(sql_conv)
            self.conexion.commit()
            return 'ok'
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return f'Error: {e}'

    def ejecutar_transaccion(self, operaciones):
        """
        Ejecuta múltiples sentencias dentro de una transacción atómica.
        operaciones: lista de tuplas (sql, datos)
        """
        cursor = self.conexion.cursor()
        try:
            ultimo_id = None
            if self.db_type == "mysql":
                self.conexion.start_transaction()
            for sql, datos in operaciones:
                sql_conv = self._formatear_sql(sql)
                if datos:
                    cursor.execute(sql_conv, tuple(datos) if isinstance(datos, (list, tuple)) else datos)
                else:
                    cursor.execute(sql_conv)
                if cursor.lastrowid:
                    ultimo_id = cursor.lastrowid
            self.conexion.commit()
            return {'status': 'ok', 'ultimo_id': ultimo_id}
        except Exception as e:
            self.conexion.rollback()
            print(f"Error en transaccion: {e}")
            return {'status': 'error', 'msg': str(e)}

    def obtener_ultimo_id(self):
        cursor = self.conexion.cursor()
        if self.db_type == "sqlite":
            cursor.execute("SELECT last_insert_rowid()")
            row = cursor.fetchone()
            return row[0] if row else None
        else:
            return cursor.lastrowid