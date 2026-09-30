import conexion

db = conexion.Conexion()


class crud_tarifas:
    def consultar(self, idProducto=None):
        if idProducto:
            return db.consultar(
                "SELECT * FROM tarifas WHERE idProducto = %s AND activa = 1 ORDER BY desde ASC",
                (idProducto,)
            )
        return db.consultar("SELECT * FROM tarifas WHERE activa = 1 ORDER BY idProducto, desde ASC")

    def obtener_por_id(self, idTarifa):
        filas = db.consultar("SELECT * FROM tarifas WHERE idTarifa = %s", (idTarifa,))
        return filas[0] if filas else None

    def administrar(self, datos):
        accion = datos.get('accion', 'nuevo')
        try:
            if accion == 'nuevo':
                sql = """
                    INSERT INTO tarifas (idProducto, desde, hasta, precio_base, adicional, porcentaje, fecha_vigencia_desde, version, activa)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
                """
                valores = (
                    datos['idProducto'],
                    datos['desde'],
                    datos['hasta'],
                    datos['precio_base'],
                    datos.get('adicional', 0.0),
                    datos.get('porcentaje', 0.0),
                    datos['fecha_vigencia_desde'],
                    datos.get('version', 'v1')
                )
            elif accion == 'modificar':
                sql = """
                    UPDATE tarifas SET desde=%s, hasta=%s, precio_base=%s, adicional=%s, porcentaje=%s, fecha_vigencia_desde=%s, version=%s
                    WHERE idTarifa=%s
                """
                valores = (
                    datos['desde'],
                    datos['hasta'],
                    datos['precio_base'],
                    datos.get('adicional', 0.0),
                    datos.get('porcentaje', 0.0),
                    datos['fecha_vigencia_desde'],
                    datos.get('version', 'v1'),
                    datos['idTarifa']
                )
            else:
                sql = "UPDATE tarifas SET activa = 0 WHERE idTarifa = %s"
                valores = (datos['idTarifa'],)

            return db.ejecutar(sql, valores)
        except Exception as e:
            return f"Error al administrar tarifa: {e}"
