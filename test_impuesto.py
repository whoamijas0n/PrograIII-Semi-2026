import unittest
from decimal import Decimal
import conexion
import crud_clientes
import crud_tarifas
import crud_periodos
import crud_cobros
from calculo_impuesto import CalculadorImpuesto, ErrorReglaNegocio


class TestImpuestoActividadesEconomicas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = conexion.Conexion()
        cls.crudTarifas = crud_tarifas.crud_tarifas()
        cls.crudPeriodos = crud_periodos.crud_periodos()
        cls.crudCobros = crud_cobros.crud_cobros()
        cls.crudClientes = crud_clientes.crud_clientes()

        # Obtener tarifas de Comercio (idProducto = 1)
        cls.tarifas_comercio = cls.crudTarifas.consultar(1)
        cls.tarifas_industria = cls.crudTarifas.consultar(2)

    def test_ca01_balance_545(self):
        """
        CA 01: Balance de 545.00 -> El sistema asigna 4.50 con la fórmula por bloque completo.
        Rango: 500.01 a 1,000.00 (Base 1.50, Adicional 3.00)
        Excedente = 545.00 - 500.01 = 44.99 -> Bloques = CEIL(44.99/1000) = 1
        1.50 + 1 * 3.00 = 4.50
        """
        tarifa = CalculadorImpuesto.seleccionar_tarifa(545.00, self.tarifas_comercio)
        calc = CalculadorImpuesto.calcular_impuesto_mensual(545.00, tarifa)
        self.assertEqual(calc["precio_mensual_redondeado"], 4.50)
        self.assertEqual(calc["bloques"], 1)
        self.assertEqual(calc["rango_desde"], 500.01)

    def test_ca02_balance_550(self):
        """
        CA 02: Balance de 550.00 -> El sistema asigna 4.50.
        Excedente = 550.00 - 500.01 = 49.99 -> Bloques = 1
        1.50 + 1 * 3.00 = 4.50
        """
        tarifa = CalculadorImpuesto.seleccionar_tarifa(550.00, self.tarifas_comercio)
        calc = CalculadorImpuesto.calcular_impuesto_mensual(550.00, tarifa)
        self.assertEqual(calc["precio_mensual_redondeado"], 4.50)
        self.assertEqual(calc["bloques"], 1)

    def test_ca03_balance_500(self):
        """
        CA 03: Balance de 500.00 -> El sistema selecciona el primer rango (0.01 a 500.00, Precio base 1.50).
        """
        tarifa = CalculadorImpuesto.seleccionar_tarifa(500.00, self.tarifas_comercio)
        self.assertEqual(float(tarifa["desde"]), 0.01)
        self.assertEqual(float(tarifa["hasta"]), 500.00)
        calc = CalculadorImpuesto.calcular_impuesto_mensual(500.00, tarifa)
        self.assertEqual(calc["precio_mensual_redondeado"], 1.50)

    def test_ca04_balance_500_01(self):
        """
        CA 04: Balance de 500.01 -> El sistema selecciona el segundo rango (500.01 a 1000.00)
        y aplica el precio base sin bloque adicional (1.50).
        """
        tarifa = CalculadorImpuesto.seleccionar_tarifa(500.01, self.tarifas_comercio)
        self.assertEqual(float(tarifa["desde"]), 500.01)
        calc = CalculadorImpuesto.calcular_impuesto_mensual(500.01, tarifa)
        self.assertEqual(calc["bloques"], 0)
        self.assertEqual(calc["precio_mensual_redondeado"], 1.50)

    def test_ca05_cambio_balance_recalculo_inmediato(self):
        """
        CA 05: Cambio de balance -> El precio se recalcula inmediatamente en un período nuevo.
        """
        preview_1 = self.crudPeriodos.calcular_vista_previa({
            "idCliente": 2,
            "idProducto": 1,
            "balance": 500.00,
            "fecha_desde": "2027-01-01",
            "fecha_hasta": "2028-01-01"
        })
        self.assertEqual(preview_1["status"], "ok")
        self.assertEqual(preview_1["precio_mensual_redondeado"], 1.50)

        preview_2 = self.crudPeriodos.calcular_vista_previa({
            "idCliente": 2,
            "idProducto": 1,
            "balance": 545.00,
            "fecha_desde": "2027-01-01",
            "fecha_hasta": "2028-01-01"
        })
        self.assertEqual(preview_2["status"], "ok")
        self.assertEqual(preview_2["precio_mensual_redondeado"], 4.50)

    def test_ca06_ca07_conservacion_periodo_anterior_y_renovacion(self):
        """
        CA 06: Cambio anual crea período nuevo y conserva el anterior.
        CA 07: Balance sin cambio permite otro período anual con el mismo monto y precio.
        """
        info = self.crudPeriodos.consultar_por_cliente(2, 1)
        periodos = info["periodos"]
        # Debe haber al menos los períodos del ejemplo histórico
        self.assertGreaterEqual(len(periodos), 4)
        # Verificar que el de 2023 existe con 545.00 y el de 2024 existe con 550.00
        anios = {str(p["fecha_desde"])[:4]: float(p["balance"]) for p in periodos}
        self.assertIn("2023", anios)
        self.assertIn("2024", anios)
        self.assertEqual(anios["2023"], 545.00)
        self.assertEqual(anios["2024"], 550.00)

    def test_ca08_periodo_historico_2022_conserva_2_10(self):
        """
        CA 08: Período histórico 2022 conserva el precio registrado de 2.10 (RF 14).
        """
        info = self.crudPeriodos.consultar_por_cliente(2, 1)
        p_2022 = next(p for p in info["periodos"] if str(p["fecha_desde"]).startswith("2022"))
        self.assertEqual(float(p_2022["precio_mensual"]), 2.10)
        self.assertEqual(p_2022["version_formula"], "PROPORCIONAL_HISTORICA")

    def test_ca09_total_administrativo_visual(self):
        """
        RF 21 / Sección 7: La suma visual de filas históricas es 20.10.
        2.10 + 4.50 + 4.50 + 4.50 + 4.50 = 20.10.
        """
        info = self.crudPeriodos.consultar_por_cliente(2, 1)
        self.assertEqual(info["total_administrativo"], 20.10)
        self.assertEqual(info["impuesto_vigente"], 4.50)

    def test_ca10_balance_entre_6000_01_y_8000_rechazado(self):
        """
        CA 10: Balance entre 6,000.01 y 8,000.00 se rechaza con mensaje
        'No existe una tarifa configurada para el balance indicado.'
        """
        with self.assertRaises(ErrorReglaNegocio) as ctx:
            CalculadorImpuesto.seleccionar_tarifa(7000.00, self.tarifas_comercio)
        self.assertEqual(str(ctx.exception), "No existe una tarifa configurada para el balance indicado.")

    def test_ca11_productos_comercio_e_industria_separados(self):
        """
        CA 11: Productos 11801 y 11802 tienen tarifas independientes y validadas expresamente.
        """
        prod_comercio = self.crudPeriodos.consultar_producto_por_id(1)
        prod_industria = self.crudPeriodos.consultar_producto_por_id(2)
        self.assertEqual(prod_comercio["codigo"], "11801")
        self.assertEqual(prod_industria["codigo"], "11802")
        self.assertGreater(len(self.tarifas_comercio), 0)
        self.assertGreater(len(self.tarifas_industria), 0)

    def test_ca12_cobro_durante_2025_aplica_4_50(self):
        """
        CA 12: Cobro durante 2025 solo utiliza el período 2025 a 2026 y el precio mensual de 4.50
        (NO la suma administrativa de 20.10).
        """
        sim = self.crudCobros.simular_cobro(2, "2025-06-15", meses=1)
        self.assertEqual(sim["status"], "ok")
        self.assertEqual(sim["total"], 4.50)
        self.assertNotEqual(sim["total"], 20.10)

    def test_ca13_tarifa_porcentaje_decimal(self):
        """
        CA 13: Porcentaje de 1.50 -> El sistema utiliza 1.50 y no lo trunca a 1.
        Balance de 50,000.00 x 1.50% = 750.00.
        """
        tarifa_pct = {
            "idTarifa": 999,
            "desde": 10000.00,
            "hasta": 100000.00,
            "precio_base": 0.00,
            "adicional": 0.00,
            "porcentaje": 1.50
        }
        calc = CalculadorImpuesto.calcular_impuesto_mensual(50000.00, tarifa_pct)
        self.assertEqual(calc["precio_mensual_redondeado"], 750.00)
        self.assertEqual(calc["porcentaje"], 1.50)

    def test_ca14_periodos_superpuestos_bloqueados(self):
        """
        CA 14: Períodos superpuestos: El sistema bloquea el guardado y muestra:
        'El período indicado se superpone con un período existente.'
        """
        periodos_existentes = [
            {"fecha_desde": "2025-01-01", "fecha_hasta": "2026-01-01", "estado": "vigente"}
        ]
        with self.assertRaises(ErrorReglaNegocio) as ctx:
            CalculadorImpuesto.validar_superposicion_periodos(
                "2025-06-01", "2026-06-01", periodos_existentes
            )
        self.assertEqual(str(ctx.exception), "El período indicado se superpone con un período existente.")

        # Pero fecha_hasta coincidiendo con fecha_desde siguiente es válida (RF 05)
        valido, _ = CalculadorImpuesto.validar_superposicion_periodos(
            "2026-01-01", "2027-01-01", periodos_existentes
        )
        self.assertTrue(valido)

    def test_ca15_tarifa_inexistente_bloquea_guardado(self):
        """
        CA 15: Tarifa inexistente bloquea el guardado sin recurrir al precio general.
        """
        preview = self.crudPeriodos.calcular_vista_previa({
            "idCliente": 2,
            "idProducto": 1,
            "balance": 7500.00,  # En el hueco 6000.01 a 8000.00
            "fecha_desde": "2028-01-01",
            "fecha_hasta": "2029-01-01"
        })
        self.assertEqual(preview["status"], "error")
        self.assertEqual(preview["msg"], "No existe una tarifa configurada para el balance indicado.")

    def test_validacion_cliente_no_empresa(self):
        """
        Sección 16: Cliente no empresarial -> 'El Impuesto a las Actividades Económicas requiere un cliente de tipo empresa.'
        """
        cliente_particular = {"idCliente": 1, "nombre": "Luis Hernandez", "tipo": "particular"}
        with self.assertRaises(ErrorReglaNegocio) as ctx:
            CalculadorImpuesto.validar_cliente(cliente_particular)
        self.assertEqual(
            str(ctx.exception),
            "El Impuesto a las Actividades Económicas requiere un cliente de tipo empresa."
        )

    def test_validacion_fechas_invalidas(self):
        """
        Sección 16: Fechas inválidas -> 'La fecha Hasta debe ser posterior a la fecha Desde.'
        """
        with self.assertRaises(ErrorReglaNegocio) as ctx:
            CalculadorImpuesto.validar_fechas("2026-05-01", "2026-04-01")
        self.assertEqual(
            str(ctx.exception),
            "La fecha Hasta debe ser posterior a la fecha Desde."
        )

    def test_validacion_balance_no_positivo(self):
        """
        Sección 16: Balance vacío o no positivo -> 'Ingrese un balance mayor que cero.'
        """
        with self.assertRaises(ErrorReglaNegocio) as ctx:
            CalculadorImpuesto.validar_balance(0)
        self.assertEqual(str(ctx.exception), "Ingrese un balance mayor que cero.")


if __name__ == "__main__":
    unittest.main()
