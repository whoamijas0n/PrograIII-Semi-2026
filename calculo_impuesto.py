from decimal import Decimal, ROUND_HALF_UP
import math
from datetime import datetime


class ErrorReglaNegocio(Exception):
    def __init__(self, mensaje, codigo="ERROR_VALIDACION"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


class CalculadorImpuesto:
    @staticmethod
    def redondear_moneda(valor):
        if valor is None:
            return Decimal("0.00")
        d = Decimal(str(valor))
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def redondear_interno(valor):
        if valor is None:
            return Decimal("0.000000")
        d = Decimal(str(valor))
        return d.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

    @classmethod
    def validar_cliente(cls, cliente):
        """
        Valida que el cliente sea de tipo empresa (RF 16 / Sec 16).
        """
        if not cliente:
            raise ErrorReglaNegocio("El cliente especificado no existe.")
        tipo = str(cliente.get("tipo", "")).strip().lower()
        if tipo != "empresa":
            raise ErrorReglaNegocio(
                "El Impuesto a las Actividades Económicas requiere un cliente de tipo empresa."
            )

    @classmethod
    def validar_balance(cls, balance):
        """
        Valida que el balance sea mayor que cero (Sec 16).
        """
        try:
            monto = Decimal(str(balance))
        except Exception:
            raise ErrorReglaNegocio("Ingrese un balance mayor que cero.")

        if monto <= Decimal("0.00"):
            raise ErrorReglaNegocio("Ingrese un balance mayor que cero.")
        return monto

    @classmethod
    def validar_fechas(cls, desde_str, hasta_str):
        """
        Valida que fecha_hasta sea mayor que fecha_desde (RF 03 / Sec 16).
        Formato esperado: YYYY-MM-DD.
        """
        try:
            d_desde = datetime.strptime(str(desde_str).strip()[:10], "%Y-%m-%d").date()
            d_hasta = datetime.strptime(str(hasta_str).strip()[:10], "%Y-%m-%d").date()
        except Exception:
            raise ErrorReglaNegocio("Formato de fecha inválido. Utilice el formato YYYY-MM-DD.")

        if d_hasta <= d_desde:
            raise ErrorReglaNegocio("La fecha Hasta debe ser posterior a la fecha Desde.")
        return d_desde, d_hasta

    @classmethod
    def validar_producto(cls, producto):
        """
        Valida que el producto corresponda a comercio (11801) o industria (11802) (Sec 16).
        """
        if not producto:
            raise ErrorReglaNegocio("Confirme si la actividad corresponde a comercio o industria.")
        codigo = str(producto.get("codigo", "")).strip()
        if codigo not in ("11801", "11802"):
            raise ErrorReglaNegocio("Confirme si la actividad corresponde a comercio o industria.")

    @classmethod
    def validar_superposicion_periodos(cls, nuevo_desde, nuevo_hasta, periodos_existentes, id_periodo_ignorar=None):
        """
        RF 02: Intervalo semiabierto [Desde, Hasta), incluyendo Desde y excluyendo Hasta.
        RF 04: Períodos no pueden superponerse: max(d1, d2) < min(h1, h2).
        RF 05: Hasta de un período puede coincidir con Desde del siguiente.
        RF 06: Advertencia informativa si existe espacio sin cobertura.
        """
        d_nuevo, h_nuevo = cls.validar_fechas(nuevo_desde, nuevo_hasta)
        advertencias = []
        fechas_anteriores = []

        for p in periodos_existentes:
            if id_periodo_ignorar and str(p.get("idPeriodo")) == str(id_periodo_ignorar):
                continue
            # Ignorar períodos anulados o cerrados si aplicara
            if p.get("estado") == "anulado":
                continue

            d_exist, h_exist = cls.validar_fechas(p["fecha_desde"], p["fecha_hasta"])
            fechas_anteriores.append((d_exist, h_exist))

            # Verificación de traslape en [Desde, Hasta)
            inicio_max = max(d_nuevo, d_exist)
            fin_min = min(h_nuevo, h_exist)

            if inicio_max < fin_min:
                raise ErrorReglaNegocio("El período indicado se superpone con un período existente.")

        # RF 06: Verificar si existe espacio sin cobertura (hueco) con respecto al período inmediatamente anterior
        if fechas_anteriores:
            # Encontrar el período que termina antes de d_nuevo
            anteriores = [f for f in fechas_anteriores if f[1] <= d_nuevo]
            if anteriores:
                ultimo_anterior = max(anteriores, key=lambda x: x[1])
                if ultimo_anterior[1] < d_nuevo:
                    advertencias.append(
                        f"Advertencia: Existe un espacio sin cobertura entre {ultimo_anterior[1]} y {d_nuevo}."
                    )

        return True, advertencias

    @classmethod
    def seleccionar_tarifa(cls, balance, tarifas):
        """
        RF 10: TarifaDesde <= Balance <= TarifaHasta
        RF 11: Si no existe -> 'No existe una tarifa configurada para el balance indicado.'
        RF 12: Si existe más de una -> 'Existe más de una tarifa aplicable. Corrija la tabla tarifaria.'
        RF 13: Bloquear silenciosamente precio general.
        """
        monto = cls.validar_balance(balance)
        tarifas_aplicables = []

        for t in tarifas:
            desde = Decimal(str(t["desde"]))
            hasta = Decimal(str(t["hasta"]))
            if desde <= monto <= hasta:
                tarifas_aplicables.append(t)

        if len(tarifas_aplicables) == 0:
            raise ErrorReglaNegocio("No existe una tarifa configurada para el balance indicado.")
        if len(tarifas_aplicables) > 1:
            raise ErrorReglaNegocio("Existe más de una tarifa aplicable. Corrija la tabla tarifaria.")

        return tarifas_aplicables[0]

    @classmethod
    def calcular_impuesto_mensual(cls, balance, tarifa, version_formula="BLOQUES_CEIL_2026"):
        """
        Calcula el impuesto mensual según la Sección 10.
        Soporta:
        1. Tarifa porcentual: Impuesto = Balance x Porcentaje / 100
        2. Tarifa por bloques:
           - Si Balance == TarifaDesde: Bloques = 0, Impuesto = PrecioBase (CA 04)
           - Si Balance > TarifaDesde:
             Excedente = Balance - TarifaDesde
             Bloques = CEIL(Excedente / 1000)
             Impuesto = PrecioBase + (Bloques x Adicional)
        """
        monto = cls.validar_balance(balance)
        tarifa_desde = Decimal(str(tarifa["desde"]))
        tarifa_hasta = Decimal(str(tarifa["hasta"]))
        precio_base = Decimal(str(tarifa["precio_base"]))
        adicional = Decimal(str(tarifa.get("adicional", 0.00)))
        porcentaje = Decimal(str(tarifa.get("porcentaje", 0.00)))

        tipo_calculo = "bloques"
        excedente = Decimal("0.00")
        bloques = 0

        if porcentaje > Decimal("0.00"):
            tipo_calculo = "porcentual"
            impuesto_raw = monto * (porcentaje / Decimal("100.00"))
            detalle_formula = (
                f"Tarifa porcentual: Balance (${monto:,.2f}) x {porcentaje}% = "
                f"${cls.redondear_moneda(impuesto_raw):,.2f}"
            )
        else:
            tipo_calculo = "bloques"
            if monto == tarifa_desde:
                # Regla Sección 10.1 y CA 04:
                # Si el balance es exactamente igual al inicio del rango, los bloques adicionales serán cero.
                excedente = Decimal("0.00")
                bloques = 0
                impuesto_raw = precio_base
                detalle_formula = (
                    f"Rango: [${tarifa_desde:,.2f} a ${tarifa_hasta:,.2f}]. "
                    f"Balance igual al inicio del rango: Precio base ${precio_base:,.2f} (0 bloques adicionales)."
                )
            else:
                excedente = monto - tarifa_desde
                # Excedente dividido por 1000 con redondeo hacia arriba CEIL
                bloques = math.ceil(float(excedente) / 1000.0)
                impuesto_raw = precio_base + (Decimal(str(bloques)) * adicional)
                detalle_formula = (
                    f"Rango: [${tarifa_desde:,.2f} a ${tarifa_hasta:,.2f}]. "
                    f"Base ${precio_base:,.2f} + ({bloques} bloque(s) x ${adicional:,.2f}) = "
                    f"${cls.redondear_moneda(impuesto_raw):,.2f} (Excedente: ${excedente:,.2f})"
                )

        precio_mensual_interno = cls.redondear_interno(impuesto_raw)
        precio_mensual_redondeado = cls.redondear_moneda(impuesto_raw)

        return {
            "balance": float(monto),
            "tarifa_id": tarifa.get("idTarifa"),
            "rango_desde": float(tarifa_desde),
            "rango_hasta": float(tarifa_hasta),
            "precio_base": float(precio_base),
            "excedente": float(excedente),
            "bloques": bloques,
            "adicional": float(adicional),
            "porcentaje": float(porcentaje),
            "tipo_calculo": tipo_calculo,
            "precio_mensual": float(precio_mensual_interno),
            "precio_mensual_redondeado": float(precio_mensual_redondeado),
            "detalle_formula": detalle_formula,
            "version_formula": version_formula
        }

    @classmethod
    def calcular_cargo_cobro(cls, precio_mensual, cantidad=1.00, meses=1):
        """
        Sección 15: Cargo del período = Cantidad x Precio mensual x Meses aplicables.
        """
        p = Decimal(str(precio_mensual))
        c = Decimal(str(cantidad))
        m = Decimal(str(meses))
        cargo = p * c * m
        return cls.redondear_moneda(cargo)
