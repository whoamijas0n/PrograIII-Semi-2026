import os

def limpiar_pantalla():
    os.system('clear')

def deducciones_ley():
    limpiar_pantalla()
    print("="*70)
    print("     Cálculo de Deducciones de Ley y Sueldo Neto (ISSS, AFP, ISR)")
    print("="*70)
    while True:
        try:
            sueldo_bruto = float(input("Ingrese el sueldo nominal/bruto mensual ($): "))
            if sueldo_bruto < 0:
                print("")
                print("[!] Error: El sueldo no puede ser negativo.")
                print("")
                continue
            break
        except ValueError:
            print("")
            print("[!] Error: Ingrese un valor numérico válido.")
            print("")

    # ISSS: 3% (Tope legal de cotización sobre $1,000.00 -> Retención máxima de $30.00)
    techo_isss = 1000.00
    if sueldo_bruto > techo_isss:
        deduccion_isss = 30.00
        nota_isss = "(Tope legal alcanzado: $1,000.00)"
    else:
        deduccion_isss = sueldo_bruto * 0.03
        nota_isss = "(3.00%)"

    # AFP: 6.25% (según indicación)
    deduccion_afp = sueldo_bruto * 0.0625

    # Sueldo Gravable / Imponible para cálculo del ISR
    sueldo_gravable = sueldo_bruto - deduccion_isss - deduccion_afp

    # Tabla Oficial Mensual de Retención de ISR (Ministerio de Hacienda)
    # Tramo I:   $0.01 a $472.00     -> Sin retención (0%)
    # Tramo II:  $472.01 a $895.24   -> 10% sobre exceso de $472.00 + $17.67
    # Tramo III: $895.25 a $2,038.10 -> 20% sobre exceso de $895.24 + $60.00
    # Tramo IV:  $2,038.11 en adelante -> 30% sobre exceso de $2,038.10 + $288.57
    if sueldo_gravable <= 472.00:
        deduccion_isr = 0.0
        tramo_isr = "Tramo I: Exento de ISR (0%)"
    elif sueldo_gravable <= 895.24:
        exceso = sueldo_gravable - 472.00
        deduccion_isr = (exceso * 0.10) + 17.67
        tramo_isr = "Tramo II: 10% s/exceso $472.00 + $17.67"
    elif sueldo_gravable <= 2038.10:
        exceso = sueldo_gravable - 895.24
        deduccion_isr = (exceso * 0.20) + 60.00
        tramo_isr = "Tramo III: 20% s/exceso $895.24 + $60.00"
    else:
        exceso = sueldo_gravable - 2038.10
        deduccion_isr = (exceso * 0.30) + 288.57
        tramo_isr = "Tramo IV: 30% s/exceso $2,038.10 + $288.57"

    total_deducciones = deduccion_isss + deduccion_afp + deduccion_isr
    sueldo_neto = sueldo_bruto - total_deducciones

    # Impresión detallada del comprobante
    print("\n" + "-" * 55)
    print("             BOLETA DE PAGO / PLANILLA            ")
    print("-" * 55)
    print(f"Sueldo Nominal (Bruto):      ${sueldo_bruto:>10.2f}")
    print(f"(-) Retención ISSS:          ${deduccion_isss:>10.2f}  {nota_isss}")
    print(f"(-) Retención AFP (6.25%):   ${deduccion_afp:>10.2f}")
    print(f"(=) Sueldo Gravable (ISR):   ${sueldo_gravable:>10.2f}")
    print(f"(-) Retención ISR:           ${deduccion_isr:>10.2f}  [{tramo_isr}]")
    print("-" * 55)
    print(f"TOTAL DEDUCCIONES:           ${total_deducciones:>10.2f}")
    print(f"SUELDO NETO A RECIBIR:       ${sueldo_neto:>10.2f}")
    print("-" * 55)
    print("")
    input("Presione ENTER para continuar ")

def agua_potable():
    limpiar_pantalla()  
    print("="*60)
    print("                  Calculo de agua potable")
    print("="*60)
    while True:
        try:
            metros = float(input("Ingrese los metros cúbicos (m³) consumidos: "))
            if metros < 0:
                print("")
                print("[!] Error: El consumo no puede ser un valor negativo.")
                print("")
                continue
            break
        except ValueError:
            print("")
            print("[!] Error: Ingrese un valor numérico válido.")
            print("")

    cuota_fija = 6.00
    monto_tramo2 = 0.0
    monto_tramo3 = 0.0

    if metros <= 18:
        total_pagar = cuota_fija
        detalle = f"Consumo de {metros:.2f} m³ dentro del rango base (1 a 18 m³). Aplica solo cuota fija."
    elif metros <= 28:
        exceso_18 = metros - 18
        monto_tramo2 = exceso_18 * 0.45
        total_pagar = cuota_fija + monto_tramo2
        detalle = (f"Cuota fija ($6.00) + Exceso sobre 18 m³ ({exceso_18:.2f} m³ × $0.45 = ${monto_tramo2:.2f})")
    else: # 29 m³ en adelante
        exceso_18_a_28 = 28 - 18 # 10 m³ del tramo intermedio
        monto_tramo2 = exceso_18_a_28 * 0.45 # $4.50
        exceso_28 = metros - 28
        monto_tramo3 = exceso_28 * 0.65
        total_pagar = cuota_fija + monto_tramo2 + monto_tramo3
        detalle = (f"Cuota fija ($6.00) + Tramo 19-28 m³ (10 m³ × $0.45 = ${monto_tramo2:.2f}) "
                   f"+ Exceso sobre 28 m³ ({exceso_28:.2f} m³ × $0.65 = ${monto_tramo3:.2f})")

    print("\n" + "-" * 60)
    print("                 FACTURA DE AGUA POTABLE                ")
    print("-" * 60)
    print(f"Consumo registrado:                {metros:>8.2f} m³")
    print(f"Cuota fija base (1 - 18 m³):      ${cuota_fija:>8.2f}")
    if monto_tramo2 > 0:
        print(f"Recargo Tramo (19 - 28 m³):        ${monto_tramo2:>8.2f}")
    if monto_tramo3 > 0:
        print(f"Recargo Tramo (29 m³ en adelante): ${monto_tramo3:>8.2f}")
    print("-" * 60)
    print(f"TOTAL A PAGAR:                     ${total_pagar:>8.2f}")
    print(f"Desglose: {detalle}")
    print("-" * 60)
    print("")
    input("Presione ENTER para continuar ")
    print("")

def meses_acumulados():
    limpiar_pantalla()
    print("="*70)
    print("          Tabla de Meses Acumulados y Fórmula Matemática")
    print("="*70)
    while True:
        try:
            n = int(input("Ingrese el número de meses 'n' a generar: "))
            if n <= 0:
                print("")
                print("[!] Error: Ingrese un entero positivo mayor a 0.")
                print("")
                continue
            break
        except ValueError:
            print("")
            print("[!] Error: Ingrese un número entero válido.")
            print("")

    print("\n" + "=" * 45)
    print(f"{'MESES':<10} | {'OPERACIÓN':<18} | {'ACUMULACIÓN':<10}")
    print("=" * 45)

    acumulado_anterior = 0
    # Generación usando estructuras de repetición (Ciclo for)
    for mes in range(1, n + 1):
        acumulado_actual = mes + acumulado_anterior
        operacion = f"{mes} + {acumulado_anterior} = {acumulado_actual}"
        print(f"{mes:<10} | {operacion:<18} | {acumulado_actual:<10}")
        acumulado_anterior = acumulado_actual
    print("=" * 45)

    # Demostración de la Fórmula Matemática O(1) para evitar ciclos:
    # S_n = n * (n + 1) / 2 (Suma de los primeros n números naturales / Serie de Gauss)
    acumulado_formula = (n * (n + 1)) // 2
    print("\n>>> DEDUCCIÓN DE FÓRMULA MATEMÁTICA (Sin Ciclos) <<<")
    print(f"Fórmula: S(n) = [n * (n + 1)] / 2")
    print(f"Para n = {n}: S({n}) = [{n} × ({n} + 1)] / 2 = [{n * (n + 1)}] / 2 = {acumulado_formula}")
    print(f"Comprobación: Ciclo for ({acumulado_anterior}) == Fórmula ({acumulado_formula}) -> Coincidencia exacta.")
    print("")
    input("Presione ENTER para continuar")
    print("")

CONVERSORES = {
    "1": {
        "nombre": "Monedas",
        "tipo": "divisas",
        "unidades": {
            "1": ("USD - Dólar estadounidense", 1.0),
            "2": ("EUR - Euro", 0.92),
            "3": ("GBP - Libra esterlina", 0.78),
            "4": ("JPY - Yen japonés", 155.0),
            "5": ("CAD - Dólar canadiense", 1.36),
            "6": ("MXN - Peso mexicano", 18.20),
            "7": ("GTQ - Quetzal guatemalteco", 7.78),
            "8": ("HNL - Lempira hondureña", 24.70),
            "9": ("CRC - Colón costarricense", 520.0),
            "10": ("BRL - Real brasileño", 5.40),
            "11": ("SVC - Colón salvadoreño (histórico)", 8.75)
        }
    },
    "2": {
        "nombre": "Longitud",
        "tipo": "base_estandar",
        "unidades": {
            "1": ("Metro (m)", 1.0),
            "2": ("Kilómetro (km)", 1000.0),
            "3": ("Centímetro (cm)", 0.01),
            "4": ("Milímetro (mm)", 0.001),
            "5": ("Micrómetro (µm)", 1e-6),
            "6": ("Pulgada (in)", 0.0254),
            "7": ("Pie (ft)", 0.3048),
            "8": ("Yarda (yd)", 0.9144),
            "9": ("Milla (mi)", 1609.344),
            "10": ("Milla náutica (NM)", 1852.0),
            "11": ("Vara (Centroamérica)", 0.836)
        }
    },
    "3": {
        "nombre": "Masa",
        "tipo": "base_estandar",
        "unidades": {
            "1": ("Kilogramo (kg)", 1.0),
            "2": ("Gramo (g)", 0.001),
            "3": ("Miligramo (mg)", 1e-6),
            "4": ("Libra (lb)", 0.45359237),
            "5": ("Onza (oz)", 0.02834952),
            "6": ("Tonelada métrica (t)", 1000.0),
            "7": ("Arroba (@ = 25 lb)", 11.3398),
            "8": ("Quintal (qq = 100 lb)", 45.3592),
            "9": ("Grano (gr)", 0.00006479891),
            "10": ("Stone (st = 14 lb)", 6.350293)
        }
    },
    "4": {
        "nombre": "Almacenamiento Digital",
        "tipo": "base_estandar",
        "unidades": {
            "1": ("Bit (b)", 0.125),
            "2": ("Byte (B)", 1.0),
            "3": ("Kilobyte (KB)", 1024.0),
            "4": ("Megabyte (MB)", 1024.0**2),
            "5": ("Gigabyte (GB)", 1024.0**3),
            "6": ("Terabyte (TB)", 1024.0**4),
            "7": ("Petabyte (PB)", 1024.0**5),
            "8": ("Kibibyte (KiB)", 1024.0),
            "9": ("Mebibyte (MiB)", 1048576.0),
            "10": ("Gibibyte (GiB)", 1073741824.0)
        }
    },
    "5": {
        "nombre": "Tiempo",
        "tipo": "base_estandar",
        "unidades": {
            "1": ("Segundo (s)", 1.0),
            "2": ("Milisegundo (ms)", 0.001),
            "3": ("Minuto (min)", 60.0),
            "4": ("Hora (h)", 3600.0),
            "5": ("Día (d)", 86400.0),
            "6": ("Semana (sem)", 604800.0),
            "7": ("Mes estándar (30 días)", 2592000.0),
            "8": ("Año estándar (365 días)", 31536000.0),
            "9": ("Década (10 años)", 315360000.0),
            "10": ("Siglo (100 años)", 3153600000.0)
        }
    },
    "6": {
        "nombre": "Volumen",
        "tipo": "base_estandar",
        "unidades": {
            "1": ("Litro (L)", 1.0),
            "2": ("Mililitro (mL)", 0.001),
            "3": ("Metro cúbico (m³)", 1000.0),
            "4": ("Centímetro cúbico (cm³ / cc)", 0.001),
            "5": ("Galón estadounidense (gal US)", 3.78541),
            "6": ("Cuarto estadounidense (qt US)", 0.946353),
            "7": ("Pinta estadounidense (pt US)", 0.473176),
            "8": ("Taza estadounidense (cup US)", 0.236588),
            "9": ("Onza líquida estadounidense (fl oz)", 0.0295735),
            "10": ("Barril de petróleo (bbl)", 158.9873)
        }
    },
    "7": {
        "nombre": "Área",
        "tipo": "base_estandar",
        "unidades": {
            "1": ("Metro cuadrado (m²)", 1.0),
            "2": ("Kilómetro cuadrado (km²)", 1000000.0),
            "3": ("Hectárea (ha)", 10000.0),
            "4": ("Centímetro cuadrado (cm²)", 0.0001),
            "5": ("Pie cuadrado (ft²)", 0.092903),
            "6": ("Yarda cuadrada (yd²)", 0.836127),
            "7": ("Acre (ac)", 4046.86),
            "8": ("Manzana (mz - Centroamérica)", 6988.96),
            "9": ("Tarea (tr - El Salvador)", 437.50),
            "10": ("Vara cuadrada (v²)", 0.698896)
        }
    }
}

def modulo_conversores():
    while True:
        limpiar_pantalla()
        print("="*70)
        print("             SISTEMA DE CONVERSORES MULTI-CATEGORÍA")
        print("="*70)
        for k, v in CONVERSORES.items():
            print(f"[{k}] {v['nombre']} ({len(v['unidades'])} unidades)")
        print("[0] Volver al menú principal")

        opc = input("\nSeleccione la categoría deseada (0-7): ").strip()
        if opc == "0":
            break
        if opc not in CONVERSORES:
            print("")
            print("[!] Opción no válida. Intente de nuevo.\n")
            print("")
            continue

        limpiar_pantalla()

        cat = CONVERSORES[opc]
        print("="*55)
        print(f"\n     --- CONVERSIÓN DE {cat['nombre'].upper()} ---")
        print("="*55)
        print("")
        for num, (nombre_u, _) in cat["unidades"].items():
            print(f"  [{num:>2}] {nombre_u}")

        # Selección unidad origen
        while True:
            u_origen = input(f"\nSeleccione unidad ORIGEN (1-{len(cat['unidades'])}): ").strip()
            if u_origen in cat["unidades"]:
                break
            print("")
            print("[!] Selección inválida.")
            print("")

        # Selección unidad destino
        while True:
            u_destino = input(f"Seleccione unidad DESTINO (1-{len(cat['unidades'])}): ").strip()
            if u_destino in cat["unidades"]:
                break
            print("")
            print("[!] Selección inválida.")
            print("")

        # Entrada del valor numérico
        while True:
            try:
                valor = float(input(f"Ingrese la cantidad en {cat['unidades'][u_origen][0]}: "))
                break
            except ValueError:
                print("")
                print("[!] Ingrese un valor numérico válido.")
                print("")

        nombre_orig, factor_orig = cat["unidades"][u_origen]
        nombre_dest, factor_dest = cat["unidades"][u_destino]

        # Operación de conversión matemática
        if cat["tipo"] == "divisas":
            # Conversión de divisa: origen a USD y de USD a destino
            valor_usd = valor / factor_orig
            resultado = valor_usd * factor_dest
        else:
            # Conversión a unidad SI base (multiplicando) y a destino (dividiendo)
            valor_base = valor * factor_orig
            resultado = valor_base / factor_dest

        print("\n" + "=" * 60)
        print(f"               RESULTADO DE LA CONVERSIÓN")
        print(f"  {valor:,.4f} {nombre_orig}")
        print(f"  = {resultado:,.6f} {nombre_dest}")
        print("=" * 60 + "\n")
        print("")
        input("Presione ENTER para continuar")

def modulo_salud():
    pacientes = []
    # Capacidad estándar de atención médica en jornada laboral: 8 horas = 480 minutos
    capacidad_jornada_minutos = 480

    tipos_atencion = {
        "1": {"tipo": "Demanda Espontánea (Urgencia / Triage I)", "tiempo": 15, "prioridad": 1},
        "2": {"tipo": "Demanda Espontánea (Consulta General / Primer Episodio)", "tiempo": 15, "prioridad": 2},
        "3": {"tipo": "Demanda Programada (Control Crónico / Seguimiento)", "tiempo": 20, "prioridad": 3},
        "4": {"tipo": "Demanda Programada (Primera Vez / Dispensarización)", "tiempo": 30, "prioridad": 3},
        "5": {"tipo": "Consulta Administrativa (Emisión de Receta Repetitiva)", "tiempo": 5, "prioridad": 4}
    }

    while True:
        limpiar_pantalla()
        print("="*70)
        print("       GESTIÓN DEL TIEMPO Y LA DEMANDA EN UNIDADES DE SALUD")
        print("="*70)
        print("[1] Registrar nuevo paciente en lista de atención")
        print("[2] Visualizar cola de espera y tiempos estimados acumulados")
        print("[3] Atender al siguiente paciente en lista")
        print("[4] Reporte de saturación de agenda, capacidad y balance de demanda")
        print("[0] Volver al menú principal")

        opc = input("\nSeleccione una opción (0-4): ").strip()

        if opc == "0":
            break

        elif opc == "1":
            print("\n--- REGISTRO DE PACIENTES ---")
            nombre = input("Nombre del paciente: ").strip()
            if not nombre:
                nombre = "Paciente Anónimo"

            print("\nCatálogo de Servicios y Tiempos Estándar (Lineamientos MINSAL):")
            for k, v in tipos_atencion.items():
                print(f"  [{k}] {v['tipo']} — Tiempo estándar: {v['tiempo']} min")

            while True:
                opc_t = input("Seleccione el tipo de atención (1-5): ").strip()
                if opc_t in tipos_atencion:
                    break
                print("[!] Opción inválida.")

            servicio = tipos_atencion[opc_t]
            pacientes.append({
                "nombre": nombre,
                "tipo": servicio["tipo"],
                "tiempo": servicio["tiempo"],
                "prioridad": servicio["prioridad"],
                "atendido": False
            })
            print(f"\n[✓] Paciente '{nombre}' registrado con éxito.")
            print(f"    Servicio: {servicio['tipo']} | Tiempo estimado: {servicio['tiempo']} minutos.")

        elif opc == "2":
            print("\n--- COLA DE PACIENTES Y GESTIÓN DE TIEMPO DE ESPERA ---")
            if not pacientes:
                print("[i] No hay pacientes registrados actualmente.")
                print("")
                input("Presione ENTER para continuar ")
                continue

            tiempo_acumulado_espera = 0
            print("-" * 85)
            print(f"{'#':<3} | {'PACIENTE':<22} | {'TIPO DE ATENCIÓN':<32} | {'TIEMPO':<8} | {'TIEMPO ESPERA'}")
            print("-" * 85)
            for idx, p in enumerate(pacientes, start=1):
                if p["atendido"]:
                    estado_str = "ATENDIDO"
                else:
                    estado_str = f"{tiempo_acumulado_espera} min de espera"
                    tiempo_acumulado_espera += p["tiempo"]
                print(f"{idx:<3} | {p['nombre'][:22]:<22} | {p['tipo'][:32]:<32} | {p['tiempo']:>4} min  | {estado_str}")
            print("-" * 85)
            print(f"Tiempo total en espera acumulada: {tiempo_acumulado_espera} minutos ({tiempo_acumulado_espera/60:.2f} horas)")
            print("")
            input("Presione ENTER para continuar ")
        elif opc == "3":
            print("\n--- ATENCIÓN DE CONSULTA MÉDICA ---")
            pendientes = [p for p in pacientes if not p["atendido"]]
            if not pendientes:
                print("[i] No existen pacientes pendientes en la lista de espera.")
                print("")
                input("Presione ENTER para continuar ")
                continue

            paciente_actual = pendientes[0]
            paciente_actual["atendido"] = True
            print(f"[✓] Atendiendo a: {paciente_actual['nombre']}")
            print(f"    Motivo: {paciente_actual['tipo']}")
            print(f"    Tiempo de consulta completado: {paciente_actual['tiempo']} minutos.")
            print(f"    [Estado actualizado a ATENDIDO]")
            print("")
            input("Presione ENTER para continuar ")

        elif opc == "4":
            print("\n--- INFORME DE RENDIMIENTO Y SATURACIÓN DE LA DEMANDA ---")
            total = len(pacientes)
            if total == 0:
                print("[i] No hay pacientes registrados para generar el informe.")
                print("")
                input("Presione ENTER para continuar ")
                continue

            atendidos = sum(1 for p in pacientes if p["atendido"])
            pendientes = total - atendidos
            minutos_totales = sum(p["tiempo"] for p in pacientes)
            minutos_atendidos = sum(p["tiempo"] for p in pacientes if p["atendido"])
            minutos_pendientes = minutos_totales - minutos_atendidos

            espontanea = sum(1 for p in pacientes if "Espontánea" in p["tipo"])
            programada = sum(1 for p in pacientes if "Programada" in p["tipo"])
            administrativa = sum(1 for p in pacientes if "Administrativa" in p["tipo"])

            porcentaje_saturacion = (minutos_totales / capacidad_jornada_minutos) * 100

            print("=" * 65)
            print(f"Capacidad estándar de la jornada médica (8h): {capacidad_jornada_minutos} min")
            print(f"Demanda total requerida en agenda:           {minutos_totales} min ({minutos_totales/60:.2f} h)")
            print(f"Nivel de Saturación / Ocupación de Agenda:   {porcentaje_saturacion:.1f}%")
            print("-" * 65)
            print(f"Total Pacientes:      {total}")
            print(f"  • Atendidos:        {atendidos} ({minutos_atendidos} min de atención médica)")
            print(f"  • En Espera:        {pendientes} ({minutos_pendientes} min pendientes)")
            print("-" * 65)
            print("Estructura de la Demanda:")
            print(f"  • Demanda Espontánea:     {espontanea:>2} ({espontanea/total*100:.1f}%)")
            print(f"  • Demanda Programada:     {programada:>2} ({programada/total*100:.1f}%)")
            print(f"  • Consultas / Recetas:    {administrativa:>2} ({administrativa/total*100:.1f}%)")
            print("=" * 65)
            if porcentaje_saturacion > 100:
                print("[!] ALERTA: Sobredemanda crítica. Se excede la jornada estándar.")
            else:
                print("[✓] ESTADO: Capacidad operativa adecuada dentro de los límites del turno.")
            print("")
            input("Presione ENTER para continuar ")
        else:
            print("")
            print("[!] Opción inválida.")
            print("")

def menu_principal():
    while True:
        limpiar_pantalla()
        print("==================================================================")
        print("               SISTEMA INTEGRAL DE CONTROL Y GESTIÓN              ")
        print("==================================================================")
        print("  [1] Cálculo de Deducciones de Ley y Sueldo Neto (ISSS, AFP, ISR)")
        print("  [2] Facturación de Consumo de Agua Potable por Escalas (m³)")
        print("  [3] Tabla de Meses Acumulados y Fórmula Matemática O(1)")
        print("  [4] Sistema de Conversores")
        print("  [5] Sistema de Gestión del Tiempo y Demanda en Salud (MINSAL)")
        print("  [0] Salir del Programa")
        print("==================================================================")
        print("")
        opcion = input("escoja una opcion (0-5) ")

        if opcion == "1":
            deducciones_ley()

        elif opcion == "2":
            agua_potable()
        
        elif opcion == "3":
            meses_acumulados()

        elif opcion == "4":
            modulo_conversores()
        
        elif opcion == "5":
            modulo_salud()


        elif opcion == "0":
            print("")
            print("Saliendo del programa")
            print("")
            break


        else:
            limpiar_pantalla()
            print("")
            print("escoja una opcion valida")
            print("")

if __name__ == "__main__":
    menu_principal()