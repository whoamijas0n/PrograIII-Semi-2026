# Requerimiento funcional del cálculo del Impuesto a las Actividades Económicas

Registro anual del balance empresarial y administración histórica de períodos

|  |  |
| --- | --- |
| **Sistema** | Impuestos a las actividades económicas |
| **Tipo de documento** | Especificación funcional |
| **Versión** | 1.0 |
| **Estado** | Borrador para validación funcional |
| **Fecha** | 30 de septiembre de 2026 |

Este documento define cómo registrar el balance anual presentado por una empresa, seleccionar la tarifa aplicable, calcular el impuesto mensual y conservar sin alteraciones los resultados históricos de cada período.

# 1 Propósito y resultado esperado

El sistema deberá calcular automáticamente el Impuesto a las Actividades Económicas para clientes registrados como empresa. El cálculo se basara en el balance o activo declarado para un período anual y en la tarifa configurada para el producto aplicable. Cada declaración generara un período independiente para preservar el balance, el precio calculado y la fórmula utilizada en ese momento.

El resultado principal será un precio mensual aplicable solamente durante la vigencia del período. Los cambios posteriores del balance, de la tabla tarifaria o de la fórmula no modificarán automáticamente períodos ya facturados.

# 2 Historia de usuario

Como encargado de cuentas corrientes, quiero registrar el balance anual presentado por una empresa e indicar su período de vigencia, para que el sistema determine el impuesto mensual correspondiente y conserve los cálculos de los años anteriores sin modificarlos.

# 3 Alcance

* Registro anual del balance o activo declarado por la empresa.
* Creación y validación de períodos de vigencia.
* Selección automatica del rango tarifario.
* Cálculo automático del impuesto mensual.
* Conservación del precio histórico y de la versión tarifaria aplicada.
* Integración del período con la asignación del servicio y el proceso posterior de cobro.
* Validación separada de los productos de comercio e industria.

# 4 Definiciónes funcionales

| **Concepto** | **Definición** |
| --- | --- |
| Balance o activo | Monto anual declarado por la empresa y utilizado como base para seleccionar la tarifa. |
| Período | Intervalo de fechas durante el cual el balance y el precio calculado permanecen vigentes. |
| Precio base | Importe fijo establecido para el rango tarifario seleccionado. |
| Adicional | Valor cobrado por cada bloque de mil dólares o fracción sobre el inicio del rango. |
| Impuesto mensual | Precio calculado que se asigna al producto para el período. |
| Precio histórico | Resultado almacenado al crear el período y que no debe recalcularse retroactivamente. |

# 5 Datos requeridos

| **Campo** | **Descripción** | **Condición** |
| --- | --- | --- |
| Cliente | Empresa a la que pertenece la declaración. | Obligatorio |
| Producto | Impuesto a las Actividades Económicas aplicable. | Obligatorio |
| Desde | Fecha inicial incluida en el período. | Obligatorio |
| Hasta | Fecha final no incluida en el período. | Obligatorio |
| Monto o activo | Balance declarado por la empresa. | Mayor que cero |
| Cantidad | Cantidad asignada al impuesto. | Normalmente 1.00 |
| Precio | Impuesto mensual calculado. | Automático |
| Subtotal | Cantidad multiplicada por precio. | Automático |
| Tarifa aplicada | Rango, precio base, adicional y porcentaje utilizados. | Auditable |

# 6 Reglas de administración de períodos

| **Id** | **Regla** |
| --- | --- |
| RF 01 | Cada balance anual deberá registrarse en un período independiente. |
| RF 02 | El período se interpretará como intervalo [Desde, Hasta), incluyendo Desde y excluyendo Hasta. |
| RF 03 | La fecha Desde deberá ser menor que la fecha Hasta. |
| RF 04 | Los períodos de una misma empresa y producto no podrán superponerse. |
| RF 05 | La fecha Hasta de un período podrá coincidir con la fecha Desde del siguiente. |
| RF 06 | El sistema advertirá cuando exista un espacio sin cobertura entre períodos. |
| RF 07 | Si el balance cambia, se cerrará el período vigente y se creará uno nuevo; no se sobrescribira el anterior. |
| RF 08 | Si el balance no cambia, se permitirá registrar el nuevo período anual con el mismo monto. |
| RF 09 | Un período incluido en recibos no podrá recalcularse de forma automatica. |

# 7 Ejemplo de períodos históricos

Los períodos observados muestran declaraciónes anuales consecutivas. El balance cambia de 700.00 a 545.00 y luego permanece en 550.00 durante tres períodos, sin que los períodos anteriores desaparezcan.

**La suma visual** de los precios de esos períodos es 20.10. Este valor es solamente un total administrativo de filas históricas; no representa la mensualidad vigente ni debe cobrarse cada mes.

| **Desde** | **Hasta** | **Balance** | **Código** | **Precio** | **Estado** |
| --- | --- | --- | --- | --- | --- |
| 01/01/2022 | 01/01/2023 | $700.00 | 11801 | $2.10 | Histórico |
| 01/01/2023 | 01/01/2024 | $545.00 | 11801 | $4.50 | Histórico |
| 01/01/2024 | 01/01/2025 | $550.00 | 11801 | $4.50 | Histórico |
| 01/01/2025 | 01/01/2026 | $550.00 | 11801 | $4.50 | Histórico |
| 01/01/2026 | 01/01/2027 | $550.00 | 11801 | $4.50 | Vigente según fecha |

# 8 Tabla tarifaria proporcionada

La siguiente tabla reproduce los rangos visibles en las capturas suministradas. Los importes se expresan en dólares. Cada tarifa deberá estar asociada expresamente al producto correspondiente y a una fecha de vigencia.

| **Desde** | **Hasta** | **Precio base** | **Adicional** | **%** |
| --- | --- | --- | --- | --- |
| 0.01 | 500.00 | 1.50 | 0.00 | 0 |
| 500.01 | 1,000.00 | 1.50 | 3.00 | 0 |
| 1,000.01 | 2,000.00 | 3.00 | 3.00 | 0 |
| 2,000.01 | 3,000.00 | 6.00 | 3.00 | 0 |
| 3,000.01 | 6,000.00 | 9.00 | 2.00 | 0 |
| 8,000.01 | 18,000.00 | 15.00 | 2.00 | 0 |
| 18,000.01 | 30,000.00 | 39.00 | 2.00 | 0 |
| 30,000.01 | 60,000.00 | 63.00 | 1.00 | 0 |
| 60,000.01 | 100,000.00 | 93.00 | 0.80 | 0 |
| 100,000.01 | 200,000.00 | 125.00 | 0.70 | 0 |
| 200,000.01 | 300,000.00 | 195.00 | 0.60 | 0 |
| 300,000.01 | 400,000.00 | 255.00 | 0.45 | 0 |
| 400,000.01 | 500,000.00 | 300.00 | 0.40 | 0 |
| 500,000.01 | 1,000,000.00 | 340.00 | 0.30 | 0 |
| 1,000,000.01 | 99,999,999.99 | 490.00 | 0.18 | 0 |

# 9 Selección de la tarifa

**RF 10 Límites inclusivos**. El sistema seleccionara una única tarifa que cumpla Tarifa Desde menor o igual al Balance y Balance menor o igual a Tarifa Hasta.

**TarifaDesde <= Balance <= TarifaHasta**

**RF 11 Tarifa inexistente**. Si ningún rango contiene el balance, el período no se guardará y se mostrará el mensaje No existe una tarifa configurada para el balance indicado.

**RF 12 Tarifas superpuestas**. Si más de una tarifa contiene el mismo balance, el cálculo se bloqueará hasta corregir la configuración.

**RF 13 Precio general**. No se utilizará silenciosamente el precio general del producto cuando falte una tarifa para este impuesto.

# 10 Fórmula del impuesto

## 10 1 Tarifa por bloques

Cuando el porcentaje de la tarifa sea cero, se aplicará el precio base más un adicional por cada bloque de mil dólares o fracción sobre el inicio del rango.

Excedente = Balance - TarifaDesde  
Bloques = CEIL(Excedente / 1,000)  
**Impuesto mensual = PrecioBase + (Bloques x Adicional)**

Si el balance es exactamente igual al inicio del rango, los bloques adicionales serán cero y el impuesto será igual al precio base.

## 10 2 Ejemplo con balance de 545 00

| **Elemento** | **Resultado** |
| --- | --- |
| Balance | $545.00 |
| Rango | $500.01 a $1,000.00 |
| Precio base | $1.50 |
| Excedente | $44.99 |
| Bloques | CEIL(44.99 / 1,000) = 1 |
| Adicional | $3.00 |
| Impuesto mensual | $1.50 + (1 x $3.00) = $4.50 |

## 10 3 Ejemplo con balance de 550 00

Excedente = 550.00 - 500.01 = 49.99  
Bloques = CEIL(49.99 / 1,000) = 1  
**Impuesto mensual = 1.50 + (1 x 3.00) = $4.50**

## 10 4 Tarifa porcentual

Cuando el porcentaje sea mayor que cero, el impuesto se calculara multiplicando el balance por el porcentaje decimal configurado. Los porcentajes decimales no deberán convertirse a enteros.

**Impuesto mensual = Balance x Porcentaje / 100**

Ejemplo: un balance de 50,000.00 con una tasa de 1.50 por ciento produce un impuesto mensual de 750.00.

# 11 Redondeo y precisión

* Los balances y tarifas se procesaran con tipos decimales, no con valores de punto flotante binario.
* El precio podrá conservar hasta seis decimales internamente para compatibilidad con la asignación actual.
* El importe mostrado y cobrado se redondeará a dos decimales al finalizar el cálculo.
* La cantidad normal del impuesto será 1.00 y el subtotal será Cantidad por Precio.

# 12 Conservación de cálculos históricos

El período 2022 a 2023 registra un balance de 700.00 y un precio de 2.10. Ese resultado coincide con una fórmula proporcional anterior, mientras que la fórmula vigente por bloques produciría 4.50. El valor histórico deberá conservarse y no se recalculará con la fórmula nueva.

Fórmula histórica: 1.50 + ((700.00 - 500.00) / 1,000 x 3.00)  
**Resultado histórico: $2.10**

**RF 14 Inmutabilidad histórica**. Los cambios de tarifa o fórmula se aplicarán solamente a períodos nuevos o a períodos no facturados cuya recalculación sea autorizada.

**RF 15 Trazabilidad**. Cada período guardará el precio resultante, el rango tarifario, la fórmula o versión y la fecha de cálculo.

**RF 16 Corrección retroactiva**. Toda corrección de un período facturado requerirá autorización, motivo y registro en bitácora.

# 13 Flujo funcional

1. Seleccionar un cliente registrado como empresa.
2. Seleccionar el producto de Impuesto a las Actividades Económicas que corresponda a comercio o industria.
3. Ingresar las fechas Desde y Hasta del nuevo período.
4. Ingresar el balance o activo declarado.
5. Buscar una única tarifa vigente que contenga el balance.
6. Calcular automáticamente el precio mensual y mostrar el detalle de la fórmula.
7. Solicitar confirmación del usuario antes de guardar.
8. Guardar el período, la asignación, el precio calculado y la información de auditoría.
9. Aplicar el precio solamente a los cobros cuyas fechas coincidan con la vigencia del período.

# 14 Comportamiento de la interfaz

**RF 17 Cálculo inmediato**. Al introducir o cambiar el Monto o Activo de un período nuevo, el sistema recalculará el precio de los servicios tarifados.

**RF 18 Detalle visible**. La pantalla mostrará balance, rango aplicado, precio base, excedente, bloques, adicional, porcentaje y resultado mensual.

**RF 19 Cambio de producto**. Al cambiar el producto se descartará la tarifa anterior y se calculara nuevamente con la tabla del nuevo producto.

**RF 20 Cambio de fecha**. Al cambiar la fecha de inicio se recalculará cuando corresponda una versión tarifaria diferente.

**RF 21 Total administrativo**. La pantalla distinguirá el Impuesto mensual vigente del Total referencial de períodos registrados.

# 15 Integración con el cobro

Para un recibo determinado, el sistema utilizará solamente los períodos que se superpongan con el rango de cobro. El importe del servicio se obtendrá multiplicando la cantidad por el precio mensual y por los meses aplicables dentro de la vigencia.

**Cargo del período = Cantidad x Precio mensual x Meses aplicables**

La suma histórica de 20.10 mostrada en la administración de clientes no deberá convertirse en una mensualidad. Para una fecha de 2025, por ejemplo, se utilizará el período 01/01/2025 a 01/01/2026 y su precio mensual de 4.50.

# 16 Validaciónes y mensajes

| **Validación** | **Mensaje esperado** |
| --- | --- |
| Cliente no empresarial | El Impuesto a las Actividades Económicas requiere un cliente de tipo empresa. |
| Balance vacío o no positivo | Ingrese un balance mayor que cero. |
| Fechas inválidas | La fecha Hasta debe ser posterior a la fecha Desde. |
| Período superpuesto | El período indicado se superpone con un período existente. |
| Tarifa inexistente | No existe una tarifa configurada para el balance indicado. |
| Tarifas duplicadas | Existe más de una tarifa aplicable. Corrija la tabla tarifaria. |
| Producto sin confirmar | Confirme si la actividad corresponde a comercio o industria. |
| Período facturado | El período ya fue utilizado en recibos y no puede recalcularse automáticamente. |

# 17 Auditoría y seguridad

* Registrar usuario, fecha y hora de creación o modificación del período.
* Conservar balance anterior y nuevo cuando exista una corrección autorizada.
* Registrar tarifa, fórmula, versión y precio resultante.
* Restringir la modificación retroactiva mediante permisos específicos.
* Ejecutar el guardado del cliente, período y asignación dentro de una transacción.

# 18 Puntos pendientes de aprobación

## 18 1 Producto de comercio e industria

La tabla tarifaria de las capturas aparece bajo el código 11802 y un nombre que comienza con Impuesto a las Actividades Económicas Industria. Los períodos históricos mostrados utilizan el código 11801, correspondiente a Comercio. Antes del desarrollo se debe confirmar si las tablas son distintas, si ambos productos comparten tabla o si existe un código incorrecto en las capturas.

## 18 2 Rango no visible

Debe confirmarse la tarifa aplicable a balances desde 6,000.01 hasta 8,000.00. El sistema no debe inventar una tarifa ni continuar con el precio general del producto.

## 18 3 Fórmula por bloque

Debe aprobarse expresamente que los nuevos períodos utilizarán bloques completos mediante CEIL. Esta decisión explica los precios de 4.50 para balances de 545.00 y 550.00, pero difiere del cálculo proporcional histórico de 2.10 para el balance de 700.00.

# 19 Criterios de aceptación

| **Id** | **Caso** | **Resultado esperado** |
| --- | --- | --- |
| CA 01 | Balance de 545.00 | El sistema asigna 4.50 con la fórmula por bloque completo. |
| CA 02 | Balance de 550.00 | El sistema asigna 4.50. |
| CA 03 | Balance de 500.00 | El sistema seleccióna el primer rango. |
| CA 04 | Balance de 500.01 | El sistema seleccióna el segúndo rango y aplica el precio base sin bloque adicional. |
| CA 05 | Cambio de balance | El precio se recalcula inmediatamente en un período nuevo. |
| CA 06 | Cambio anual | Se crea un período nuevo y se conserva el anterior. |
| CA 07 | Balance sin cambio | Se permite otro período anual con el mismo balance y precio. |
| CA 08 | Período histórico 2022 | Conserva el precio registrado de 2.10. |
| CA 09 | Cambio tarifario | No modifica períodos ni recibos históricos. |
| CA 10 | Balance entre 6,000.01 y 8,000.00 | Se rechaza hasta configurar el rango faltante. |
| CA 11 | Productos 11801 y 11802 | Sus tarifas no se intercambian sin configuración expresa. |
| CA 12 | Cobro durante 2025 | Solo utiliza el período 2025 a 2026 y el precio mensual de 4.50. |
| CA 13 | Porcentaje de 1.50 | El sistema utiliza 1.50 y no lo trunca a 1. |
| CA 14 | Períodos superpuestos | El sistema bloquea el guardado y muestra el conflicto. |
| CA 15 | Tarifa inexistente | El sistema bloquea el guardado sin usar el precio general. |

# 20 Aprobación funcional

La implementación podrá iniciar cuando se confirmen el producto al que pertenece la tabla tarifaria, el rango de 6,000.01 a 8,000.00 y el uso de la fórmula por bloque completo para períodos nuevos.

| **Rol** | **Nombre y firma** | **Fecha** |
| --- | --- | --- |
| Responsable de cuentas corrientes |  |  |
| Responsable de desarrollo |  |  |
| Responsable de autorización |  |  |