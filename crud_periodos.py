from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import conexion
from calculo_impuesto import CalculadorImpuesto, ErrorReglaNegocio

db = conexion.Conexion()


class crud_periodos:
    def consultar_cliente_por_id(self, idCliente):
        filas = db.consultar("SELECT * FROM clientes WHERE idCliente = %s", (idCliente,))
        return filas[0] if filas else None

    def consultar_producto_por_id(self, idProducto):
        filas = db.consultar("SELECT * FROM productos WHERE idProducto = %s", (idProducto,))
        return filas[0] if filas else None

    def consultar_tarifas_producto(self, idProducto):
        return db.consultar(
            "SELECT * FROM tarifas WHERE idProducto = %s AND activa = 1 ORDER BY desde ASC",
            (idProducto,)
        )

    def consultar_por_cliente(self, idCliente, idProducto=None):
        """
        Retorna la lista de períodos, el total administrativo y el impuesto mensual vigente (RF 21 / Sec 7).
        """
        sql = """
            SELECT p.*, prod.codigo as codigoProducto, prod.nombre as nombreProducto
            FROM periodos_actividades_economicas p
            INNER JOIN productos prod ON p.idProducto = prod.idProducto
            WHERE p.idCliente = %s
        """
        valores = [idCliente]
        if idProducto:
            sql += " AND p.idProducto = %s"
            valores.append(idProducto)

        sql += " ORDER BY p.fecha_desde ASC"
        periodos = db.consultar(sql, valores) or []

        total_administrativo = Decimal("0.00")
        impuesto_vigente = Decimal("0.00")
        periodo_vigente = None
        hoy = datetime.now().date()

        for p in periodos:
            p_mensual = Decimal(str(p["precio_mensual"]))
            total_administrativo += p_mensual

            d_desde = datetime.strptime(str(p["fecha_desde"])[:10], "%Y-%m-%d").date()
            d_hasta = datetime.strptime(str(p["fecha_hasta"])[:10], "%Y-%m-%d").date()

            # Determinar estado según vigencia de fecha respecto a hoy:
            # - Si la fecha final es menor o igual a hoy (el período ya venció): 'vencido'
            # - Si hoy se encuentra en el rango [Desde, Hasta) (año o período actual no terminado): 'vigente'
            # - Si la fecha inicial es mayor a hoy: 'futuro'
            if p.get("estado") == "cerrado":
                estado_determinado = "cerrado"
            elif d_hasta <= hoy:
                estado_determinado = "vencido"
            elif d_desde <= hoy < d_hasta:
                estado_determinado = "vigente"
                periodo_vigente = p
                impuesto_vigente = p_mensual
            else:
                estado_determinado = "futuro"

            p["estado"] = estado_determinado
            p["estado_calculado"] = estado_determinado

        # Si no hubo período que cubra hoy pero hay uno con estado 'vigente', usar ese
        if not periodo_vigente and periodos:
            for p in reversed(periodos):
                if p.get("estado") == "vigente":
                    periodo_vigente = p
                    impuesto_vigente = Decimal(str(p["precio_mensual"]))
                    break

        return {
            "periodos": periodos,
            "total_administrativo": float(total_administrativo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "impuesto_vigente": float(impuesto_vigente.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "periodo_vigente": periodo_vigente
        }

    def calcular_vista_previa(self, datos):
        """
        Cálculo inmediato y validación previa para responder a la interfaz (RF 17, RF 18).
        No persiste cambios.
        """
        try:
            idCliente = datos.get("idCliente")
            idProducto = datos.get("idProducto")
            balance = datos.get("balance")
            fecha_desde = datos.get("fecha_desde")
            fecha_hasta = datos.get("fecha_hasta")
            cantidad = Decimal(str(datos.get("cantidad", 1.00)))

            cliente = self.consultar_cliente_por_id(idCliente)
            CalculadorImpuesto.validar_cliente(cliente)

            producto = self.consultar_producto_por_id(idProducto)
            CalculadorImpuesto.validar_producto(producto)

            CalculadorImpuesto.validar_balance(balance)
            CalculadorImpuesto.validar_fechas(fecha_desde, fecha_hasta)

            # Buscar tarifas del producto
            tarifas = self.consultar_tarifas_producto(idProducto)
            tarifa_aplicable = CalculadorImpuesto.seleccionar_tarifa(balance, tarifas)

            # Validar superposiciones
            periodos_existentes = db.consultar(
                "SELECT * FROM periodos_actividades_economicas WHERE idCliente = %s AND idProducto = %s",
                (idCliente, idProducto)
            ) or []

            id_ignorar = datos.get("idPeriodo")
            _, advertencias = CalculadorImpuesto.validar_superposicion_periodos(
                fecha_desde, fecha_hasta, periodos_existentes, id_ignorar
            )

            # Calcular impuesto mensual
            calc = CalculadorImpuesto.calcular_impuesto_mensual(balance, tarifa_aplicable)
            p_mensual = Decimal(str(calc["precio_mensual"]))
            subtotal = (p_mensual * cantidad).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            calc["subtotal"] = float(subtotal)
            calc["cantidad"] = float(cantidad)
            calc["advertencias"] = advertencias
            calc["status"] = "ok"
            return calc

        except ErrorReglaNegocio as ern:
            return {"status": "error", "msg": ern.mensaje}
        except Exception as e:
            return {"status": "error", "msg": f"Error en cálculo: {str(e)}"}

    def administrar(self, datos):
        """
        Procesa operaciones de períodos dentro de transacciones atómicas (Sección 17).
        """
        accion = datos.get("accion", "nuevo")
        usuario = datos.get("usuario", "admin")

        try:
            if accion in ("nuevo", "renovar_mismo_balance", "cerrar_y_crear_nuevo"):
                # Ejecutar cálculo y validación
                preview = self.calcular_vista_previa(datos)
                if preview.get("status") != "ok":
                    return {"status": "error", "msg": preview.get("msg")}

                idCliente = datos["idCliente"]
                idProducto = datos["idProducto"]
                fecha_desde = datos["fecha_desde"]
                fecha_hasta = datos["fecha_hasta"]
                balance = float(Decimal(str(datos["balance"])))
                cantidad = float(Decimal(str(datos.get("cantidad", 1.00))))
                precio_mensual = preview["precio_mensual"]
                subtotal = preview["subtotal"]
                idTarifa = preview["tarifa_id"]
                version_formula = preview.get("version_formula", "BLOQUES_CEIL_2026")
                formula_detalle = preview.get("detalle_formula", "")
                fecha_calculo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                operaciones = []

                # RF 07: Si el balance cambia, se cierra el período vigente y se crea uno nuevo
                if accion == "cerrar_y_crear_nuevo":
                    sql_cerrar = """
                        UPDATE periodos_actividades_economicas
                        SET estado = 'cerrado', usuario_modificacion = %s, fecha_modificacion = %s
                        WHERE idCliente = %s AND idProducto = %s AND estado = 'vigente'
                    """
                    operaciones.append((sql_cerrar, (usuario, fecha_calculo, idCliente, idProducto)))

                d_desde = datetime.strptime(fecha_desde[:10], "%Y-%m-%d").date()
                d_hasta = datetime.strptime(fecha_hasta[:10], "%Y-%m-%d").date()
                hoy = datetime.now().date()

                if d_hasta <= hoy:
                    estado_insert = "vencido"
                elif d_desde <= hoy < d_hasta:
                    estado_insert = "vigente"
                else:
                    estado_insert = "futuro"

                sql_insert = """
                    INSERT INTO periodos_actividades_economicas
                    (idCliente, idProducto, idTarifa, fecha_desde, fecha_hasta, balance, cantidad,
                     precio_mensual, subtotal, version_formula, formula_detalle, estado, facturado,
                     fecha_calculo, usuario_creacion, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s)
                """
                valores_insert = (
                    idCliente, idProducto, idTarifa, fecha_desde, fecha_hasta, balance, cantidad,
                    precio_mensual, subtotal, version_formula, formula_detalle, estado_insert,
                    fecha_calculo, usuario, fecha_calculo
                )
                operaciones.append((sql_insert, valores_insert))

                res = db.ejecutar_transaccion(operaciones)
                if res.get("status") != "ok":
                    return {"status": "error", "msg": res.get("msg")}

                nuevo_id = res.get("ultimo_id")
                # Registrar en bitácora de auditoría
                sql_audit = """
                    INSERT INTO bitacora_auditoria
                    (idPeriodo, accion, balance_anterior, balance_nuevo, precio_anterior, precio_nuevo, motivo, usuario_autoriza, fecha)
                    VALUES (%s, %s, NULL, %s, NULL, %s, %s, %s, %s)
                """
                motivo = "Creación de período anual" if accion != "cerrar_y_crear_nuevo" else "Cierre por cambio de balance y creación de nuevo período"
                db.ejecutar(sql_audit, (nuevo_id, "CREACION", balance, precio_mensual, motivo, usuario, fecha_calculo))

                return {
                    "status": "ok",
                    "msg": "Período guardado con éxito.",
                    "idPeriodo": nuevo_id,
                    "advertencias": preview.get("advertencias", [])
                }

            elif accion == "corregir_autorizado":
                # RF 16: Corrección retroactiva de período facturado requiere autorización, motivo y bitácora
                idPeriodo = datos.get("idPeriodo")
                motivo = datos.get("motivo", "").strip()
                usuario_autoriza = datos.get("usuario_autoriza", "").strip()

                if not motivo:
                    return {"status": "error", "msg": "Debe especificar el motivo obligatorio de la corrección."}
                if not usuario_autoriza:
                    return {"status": "error", "msg": "Se requiere el usuario o clave de autorización para corregir un período facturado."}

                filas = db.consultar("SELECT * FROM periodos_actividades_economicas WHERE idPeriodo = %s", (idPeriodo,))
                if not filas:
                    return {"status": "error", "msg": "El período a corregir no existe."}
                periodo_actual = filas[0]

                # Recalcular con el nuevo balance
                datos_calculo = {
                    "idCliente": periodo_actual["idCliente"],
                    "idProducto": periodo_actual["idProducto"],
                    "balance": datos.get("balance"),
                    "fecha_desde": periodo_actual["fecha_desde"],
                    "fecha_hasta": periodo_actual["fecha_hasta"],
                    "cantidad": periodo_actual["cantidad"],
                    "idPeriodo": idPeriodo
                }
                preview = self.calcular_vista_previa(datos_calculo)
                if preview.get("status") != "ok":
                    return {"status": "error", "msg": preview.get("msg")}

                nuevo_balance = float(Decimal(str(datos["balance"])))
                nuevo_precio = preview["precio_mensual"]
                nuevo_subtotal = preview["subtotal"]
                fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                operaciones = [
                    ("""
                        UPDATE periodos_actividades_economicas
                        SET balance = %s, precio_mensual = %s, subtotal = %s, formula_detalle = %s,
                            usuario_modificacion = %s, fecha_modificacion = %s
                        WHERE idPeriodo = %s
                    """, (nuevo_balance, nuevo_precio, nuevo_subtotal, preview.get("detalle_formula"), usuario_autoriza, fecha_ahora, idPeriodo)),
                    ("""
                        INSERT INTO bitacora_auditoria
                        (idPeriodo, accion, balance_anterior, balance_nuevo, precio_anterior, precio_nuevo, motivo, usuario_autoriza, fecha)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (idPeriodo, "CORRECCION_AUTORIZADA", periodo_actual["balance"], nuevo_balance, periodo_actual["precio_mensual"], nuevo_precio, motivo, usuario_autoriza, fecha_ahora))
                ]

                res = db.ejecutar_transaccion(operaciones)
                if res.get("status") != "ok":
                    return {"status": "error", "msg": res.get("msg")}
                return {"status": "ok", "msg": "Período corregido y auditado exitosamente."}

            elif accion == "modificar_no_facturado":
                # RF 09: Si el período ya fue utilizado en recibos, bloquear recálculo automático
                idPeriodo = datos.get("idPeriodo")
                filas = db.consultar("SELECT * FROM periodos_actividades_economicas WHERE idPeriodo = %s", (idPeriodo,))
                if not filas:
                    return {"status": "error", "msg": "El período no existe."}
                periodo_actual = filas[0]
                if periodo_actual.get("facturado") == 1:
                    return {
                        "status": "error",
                        "msg": "El período ya fue utilizado en recibos y no puede recalcularse automáticamente."
                    }

                preview = self.calcular_vista_previa(datos)
                if preview.get("status") != "ok":
                    return {"status": "error", "msg": preview.get("msg")}

                nuevo_balance = float(Decimal(str(datos["balance"])))
                nuevo_precio = preview["precio_mensual"]
                nuevo_subtotal = preview["subtotal"]
                fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                sql = """
                    UPDATE periodos_actividades_economicas
                    SET balance = %s, precio_mensual = %s, subtotal = %s, formula_detalle = %s,
                        usuario_modificacion = %s, fecha_modificacion = %s
                    WHERE idPeriodo = %s
                """
                res = db.ejecutar(sql, (nuevo_balance, nuevo_precio, nuevo_subtotal, preview.get("detalle_formula"), usuario, fecha_ahora, idPeriodo))
                if res != "ok":
                    return {"status": "error", "msg": res}
                return {"status": "ok", "msg": "Período actualizado con éxito."}

            else:
                return {"status": "error", "msg": f"Acción desconocida: {accion}"}

        except Exception as e:
            return {"status": "error", "msg": f"Error al administrar período: {str(e)}"}

    def consultar_auditoria(self, idPeriodo):
        return db.consultar(
            "SELECT * FROM bitacora_auditoria WHERE idPeriodo = %s ORDER BY fecha DESC",
            (idPeriodo,)
        )
