from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import conexion
from calculo_impuesto import CalculadorImpuesto, ErrorReglaNegocio

db = conexion.Conexion()


class crud_cobros:
    def simular_cobro(self, idCliente, fecha_cobro, meses=1):
        """
        Implementa la Sección 15 y Criterio de Aceptación CA 12:
        Para una fecha determinada (ej. 2025), utiliza el período activo que cubre esa fecha
        (ej. 01/01/2025 a 01/01/2026 con precio mensual de 4.50), y NO la suma histórica de 20.10.
        """
        try:
            d_cobro = datetime.strptime(str(fecha_cobro).strip()[:10], "%Y-%m-%d").date()
        except Exception:
            return {"status": "error", "msg": "Fecha de cobro inválida. Use formato YYYY-MM-DD."}

        # Obtener períodos del cliente
        sql = """
            SELECT p.*, prod.codigo as codigoProducto, prod.nombre as nombreProducto
            FROM periodos_actividades_economicas p
            INNER JOIN productos prod ON p.idProducto = prod.idProducto
            WHERE p.idCliente = %s
            ORDER BY p.fecha_desde ASC
        """
        periodos = db.consultar(sql, (idCliente,)) or []

        periodos_aplicables = []
        total_cargo = Decimal("0.00")

        for p in periodos:
            d_desde = datetime.strptime(str(p["fecha_desde"])[:10], "%Y-%m-%d").date()
            d_hasta = datetime.strptime(str(p["fecha_hasta"])[:10], "%Y-%m-%d").date()

            # Intervalo semiabierto [Desde, Hasta)
            if d_desde <= d_cobro < d_hasta:
                precio_m = Decimal(str(p["precio_mensual"]))
                cant = Decimal(str(p["cantidad"]))
                m_cobro = Decimal(str(meses))
                cargo = precio_m * cant * m_cobro
                total_cargo += cargo

                periodos_aplicables.append({
                    "idPeriodo": p["idPeriodo"],
                    "producto": f"{p['codigoProducto']} - {p['nombreProducto']}",
                    "vigencia": f"{d_desde} al {d_hasta}",
                    "precio_mensual": float(CalculadorImpuesto.redondear_moneda(precio_m)),
                    "cantidad": float(cant),
                    "meses": int(meses),
                    "cargo": float(CalculadorImpuesto.redondear_moneda(cargo))
                })

        if not periodos_aplicables:
            return {
                "status": "warning",
                "msg": f"No se encontró un período vigente para la fecha {fecha_cobro}.",
                "cargos": [],
                "total": 0.00
            }

        return {
            "status": "ok",
            "idCliente": idCliente,
            "fecha_cobro": str(d_cobro),
            "meses": meses,
            "cargos": periodos_aplicables,
            "total": float(CalculadorImpuesto.redondear_moneda(total_cargo)),
            "nota": "Se cobró exclusivamente según el período vigente aplicable a la fecha, no sobre el total histórico acumulado (Sección 15)."
        }

    def facturar(self, idCliente, fecha_cobro, meses=1):
        """
        Emite el recibo, registra el detalle y marca los períodos aplicados como 'facturado = 1' (RF 09 / Sec 15).
        """
        sim = self.simular_cobro(idCliente, fecha_cobro, meses)
        if sim.get("status") != "ok":
            return sim

        total = sim["total"]
        fecha_emision = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        periodo_cobro_desde = fecha_cobro
        periodo_cobro_hasta = fecha_cobro

        operaciones = [
            ("""
                INSERT INTO recibos (idCliente, fecha_emision, periodo_cobro_desde, periodo_cobro_hasta, total)
                VALUES (%s, %s, %s, %s, %s)
            """, (idCliente, fecha_emision, periodo_cobro_desde, periodo_cobro_hasta, total))
        ]

        res = db.ejecutar_transaccion(operaciones)
        if res.get("status") != "ok":
            return {"status": "error", "msg": res.get("msg")}

        idRecibo = res.get("ultimo_id")

        operaciones_detalle = []
        for c in sim["cargos"]:
            sql_det = """
                INSERT INTO detalles_recibo (idRecibo, idPeriodo, idProducto, meses_aplicables, precio_mensual, subtotal)
                VALUES (%s, %s, (SELECT idProducto FROM periodos_actividades_economicas WHERE idPeriodo = %s), %s, %s, %s)
            """
            operaciones_detalle.append((sql_det, (idRecibo, c["idPeriodo"], c["idPeriodo"], c["meses"], c["precio_mensual"], c["cargo"])))

            # Marcar período como facturado (RF 09 / RF 16)
            sql_upd = "UPDATE periodos_actividades_economicas SET facturado = 1 WHERE idPeriodo = %s"
            operaciones_detalle.append((sql_upd, (c["idPeriodo"],)))

        res_det = db.ejecutar_transaccion(operaciones_detalle)
        if res_det.get("status") != "ok":
            return {"status": "error", "msg": res_det.get("msg")}

        return {
            "status": "ok",
            "msg": f"Recibo #{idRecibo} emitido por un total de ${total:.2f}. Los períodos correspondientes han sido marcados como facturados.",
            "idRecibo": idRecibo,
            "total": total
        }

    def consultar_recibos(self, idCliente=None):
        sql = """
            SELECT r.*, c.nombre as nombreCliente
            FROM recibos r
            INNER JOIN clientes c ON r.idCliente = c.idCliente
        """
        valores = []
        if idCliente:
            sql += " WHERE r.idCliente = %s"
            valores.append(idCliente)
        sql += " ORDER BY r.fecha_emision DESC"
        return db.consultar(sql, valores if valores else None) or []
