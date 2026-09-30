-- phpMyAdmin SQL Dump
-- Database: `db_sistema_impuestos`

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- --------------------------------------------------------

--
-- Table structure for table `clientes`
--

CREATE TABLE IF NOT EXISTS `clientes` (
  `idCliente` int(10) NOT NULL AUTO_INCREMENT,
  `codigo` char(10) NOT NULL,
  `nombre` char(100) NOT NULL,
  `direccion` char(150) NOT NULL,
  `telefono` char(10) NOT NULL,
  `email` char(150) NOT NULL,
  `tipo` char(10) NOT NULL DEFAULT 'particular',
  PRIMARY KEY (`idCliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `clientes`
--

INSERT INTO `clientes` (`idCliente`, `codigo`, `nombre`, `direccion`, `telefono`, `email`, `tipo`) VALUES
(1, '001', 'Luis Hernandez', 'Usulutan', '4545-3256', 'luishernandez@ugb.edu.sv', 'particular'),
(2, '002', 'Empresa Comercial San Salvador S.A. de C.V.', 'San Salvador', '2225-8900', 'contacto@comercialsansalvador.com', 'empresa');

-- --------------------------------------------------------

--
-- Table structure for table `productos`
--

CREATE TABLE IF NOT EXISTS `productos` (
  `idProducto` int(10) NOT NULL AUTO_INCREMENT,
  `codigo` char(10) NOT NULL UNIQUE,
  `nombre` varchar(150) NOT NULL,
  `tipo` varchar(50) NOT NULL DEFAULT 'impuesto',
  `precio_general` decimal(12,4) NOT NULL DEFAULT 0.0000,
  PRIMARY KEY (`idProducto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `productos`
--

INSERT INTO `productos` (`idProducto`, `codigo`, `nombre`, `tipo`, `precio_general`) VALUES
(1, '11801', 'Impuesto a las Actividades Económicas Comercio', 'impuesto', 0.0000),
(2, '11802', 'Impuesto a las Actividades Económicas Industria', 'impuesto', 0.0000);

-- --------------------------------------------------------

--
-- Table structure for table `tarifas`
--

CREATE TABLE IF NOT EXISTS `tarifas` (
  `idTarifa` int(10) NOT NULL AUTO_INCREMENT,
  `idProducto` int(10) NOT NULL,
  `desde` decimal(14,2) NOT NULL,
  `hasta` decimal(14,2) NOT NULL,
  `precio_base` decimal(12,4) NOT NULL,
  `adicional` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `porcentaje` decimal(6,2) NOT NULL DEFAULT 0.00,
  `fecha_vigencia_desde` date NOT NULL,
  `fecha_vigencia_hasta` date DEFAULT NULL,
  `version` varchar(20) NOT NULL DEFAULT 'v1',
  `activa` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`idTarifa`),
  KEY `idProducto` (`idProducto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `tarifas` (Sección 8 de la especificación para 11801 y 11802)
-- Se respeta el vacío entre 6,000.01 y 8,000.00 según Sección 18.2 / CA 10
--

INSERT INTO `tarifas` (`idTarifa`, `idProducto`, `desde`, `hasta`, `precio_base`, `adicional`, `porcentaje`, `fecha_vigencia_desde`, `version`, `activa`) VALUES
(1, 1, 0.01, 500.00, 1.5000, 0.0000, 0.00, '2022-01-01', 'v1', 1),
(2, 1, 500.01, 1000.00, 1.5000, 3.0000, 0.00, '2022-01-01', 'v1', 1),
(3, 1, 1000.01, 2000.00, 3.0000, 3.0000, 0.00, '2022-01-01', 'v1', 1),
(4, 1, 2000.01, 3000.00, 6.0000, 3.0000, 0.00, '2022-01-01', 'v1', 1),
(5, 1, 3000.01, 6000.00, 9.0000, 2.0000, 0.00, '2022-01-01', 'v1', 1),
(6, 1, 8000.01, 18000.00, 15.0000, 2.0000, 0.00, '2022-01-01', 'v1', 1),
(7, 1, 18000.01, 30000.00, 39.0000, 2.0000, 0.00, '2022-01-01', 'v1', 1),
(8, 1, 30000.01, 60000.00, 63.0000, 1.0000, 0.00, '2022-01-01', 'v1', 1),
(9, 1, 60000.01, 100000.00, 93.0000, 0.8000, 0.00, '2022-01-01', 'v1', 1),
(10, 1, 100000.01, 200000.00, 125.0000, 0.7000, 0.00, '2022-01-01', 'v1', 1),
(11, 1, 200000.01, 300000.00, 195.0000, 0.6000, 0.00, '2022-01-01', 'v1', 1),
(12, 1, 300000.01, 400000.00, 255.0000, 0.4500, 0.00, '2022-01-01', 'v1', 1),
(13, 1, 400000.01, 500000.00, 300.0000, 0.4000, 0.00, '2022-01-01', 'v1', 1),
(14, 1, 500000.01, 1000000.00, 340.0000, 0.3000, 0.00, '2022-01-01', 'v1', 1),
(15, 1, 1000000.01, 99999999.99, 490.0000, 0.1800, 0.00, '2022-01-01', 'v1', 1),
-- Producto 2 (Industria 11802)
(16, 2, 0.01, 500.00, 1.5000, 0.0000, 0.00, '2022-01-01', 'v1', 1),
(17, 2, 500.01, 1000.00, 1.5000, 3.0000, 0.00, '2022-01-01', 'v1', 1),
(18, 2, 1000.01, 2000.00, 3.0000, 3.0000, 0.00, '2022-01-01', 'v1', 1),
(19, 2, 2000.01, 3000.00, 6.0000, 3.0000, 0.00, '2022-01-01', 'v1', 1),
(20, 2, 3000.01, 6000.00, 9.0000, 2.0000, 0.00, '2022-01-01', 'v1', 1),
(21, 2, 8000.01, 18000.00, 15.0000, 2.0000, 0.00, '2022-01-01', 'v1', 1),
(22, 2, 18000.01, 30000.00, 39.0000, 2.0000, 0.00, '2022-01-01', 'v1', 1),
(23, 2, 30000.01, 60000.00, 63.0000, 1.0000, 0.00, '2022-01-01', 'v1', 1),
(24, 2, 60000.01, 100000.00, 93.0000, 0.8000, 0.00, '2022-01-01', 'v1', 1),
(25, 2, 100000.01, 200000.00, 125.0000, 0.7000, 0.00, '2022-01-01', 'v1', 1),
(26, 2, 200000.01, 300000.00, 195.0000, 0.6000, 0.00, '2022-01-01', 'v1', 1),
(27, 2, 300000.01, 400000.00, 255.0000, 0.4500, 0.00, '2022-01-01', 'v1', 1),
(28, 2, 400000.01, 500000.00, 300.0000, 0.4000, 0.00, '2022-01-01', 'v1', 1),
(29, 2, 500000.01, 1000000.00, 340.0000, 0.3000, 0.00, '2022-01-01', 'v1', 1),
(30, 2, 1000000.01, 99999999.99, 490.0000, 0.1800, 0.00, '2022-01-01', 'v1', 1);

-- --------------------------------------------------------

--
-- Table structure for table `periodos_actividades_economicas`
--

CREATE TABLE IF NOT EXISTS `periodos_actividades_economicas` (
  `idPeriodo` int(10) NOT NULL AUTO_INCREMENT,
  `idCliente` int(10) NOT NULL,
  `idProducto` int(10) NOT NULL,
  `idTarifa` int(10) DEFAULT NULL,
  `fecha_desde` date NOT NULL,
  `fecha_hasta` date NOT NULL,
  `balance` decimal(14,2) NOT NULL,
  `cantidad` decimal(10,2) NOT NULL DEFAULT 1.00,
  `precio_mensual` decimal(14,6) NOT NULL,
  `subtotal` decimal(14,2) NOT NULL,
  `version_formula` varchar(50) NOT NULL DEFAULT 'BLOQUES_CEIL_2026',
  `formula_detalle` text DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'vigente',
  `facturado` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_calculo` datetime NOT NULL,
  `usuario_creacion` varchar(50) NOT NULL DEFAULT 'admin',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_modificacion` varchar(50) DEFAULT NULL,
  `fecha_modificacion` datetime DEFAULT NULL,
  PRIMARY KEY (`idPeriodo`),
  KEY `idCliente` (`idCliente`),
  KEY `idProducto` (`idProducto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Semilla del ejemplo histórico de la Sección 7 para cliente 2 (Empresa)
-- Suma histórica administrativa: 2.10 + 4.50 + 4.50 + 4.50 + 4.50 = 20.10
--

INSERT INTO `periodos_actividades_economicas` 
(`idPeriodo`, `idCliente`, `idProducto`, `idTarifa`, `fecha_desde`, `fecha_hasta`, `balance`, `cantidad`, `precio_mensual`, `subtotal`, `version_formula`, `formula_detalle`, `estado`, `facturado`, `fecha_calculo`) VALUES
(1, 2, 1, 2, '2022-01-01', '2023-01-01', 700.00, 1.00, 2.100000, 2.10, 'PROPORCIONAL_HISTORICA', 'Fórmula histórica: 1.50 + ((700.00 - 500.00) / 1000 * 3.00) = $2.10', 'historico', 1, '2022-01-01 10:00:00'),
(2, 2, 1, 2, '2023-01-01', '2024-01-01', 545.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'historico', 1, '2023-01-01 10:00:00'),
(3, 2, 1, 2, '2024-01-01', '2025-01-01', 550.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'historico', 1, '2024-01-01 10:00:00'),
(4, 2, 1, 2, '2025-01-01', '2026-01-01', 550.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'historico', 0, '2025-01-01 10:00:00'),
(5, 2, 1, 2, '2026-01-01', '2027-01-01', 550.00, 1.00, 4.500000, 4.50, 'BLOQUES_CEIL_2026', 'Bloques CEIL: 1.50 + (1 * 3.00) = $4.50', 'vigente', 0, '2026-01-01 10:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `bitacora_auditoria`
--

CREATE TABLE IF NOT EXISTS `bitacora_auditoria` (
  `idAuditoria` int(10) NOT NULL AUTO_INCREMENT,
  `idPeriodo` int(10) NOT NULL,
  `accion` varchar(50) NOT NULL,
  `balance_anterior` decimal(14,2) DEFAULT NULL,
  `balance_nuevo` decimal(14,2) DEFAULT NULL,
  `precio_anterior` decimal(14,6) DEFAULT NULL,
  `precio_nuevo` decimal(14,6) DEFAULT NULL,
  `motivo` text DEFAULT NULL,
  `usuario_autoriza` varchar(50) DEFAULT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idAuditoria`),
  KEY `idPeriodo` (`idPeriodo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `recibos` y `detalles_recibo` (Cobro Sección 15)
--

CREATE TABLE IF NOT EXISTS `recibos` (
  `idRecibo` int(10) NOT NULL AUTO_INCREMENT,
  `idCliente` int(10) NOT NULL,
  `fecha_emision` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `periodo_cobro_desde` date NOT NULL,
  `periodo_cobro_hasta` date NOT NULL,
  `total` decimal(14,2) NOT NULL,
  PRIMARY KEY (`idRecibo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `detalles_recibo` (
  `idDetalle` int(10) NOT NULL AUTO_INCREMENT,
  `idRecibo` int(10) NOT NULL,
  `idPeriodo` int(10) NOT NULL,
  `idProducto` int(10) NOT NULL,
  `meses_aplicables` int(4) NOT NULL DEFAULT 1,
  `precio_mensual` decimal(14,6) NOT NULL,
  `subtotal` decimal(14,2) NOT NULL,
  PRIMARY KEY (`idDetalle`),
  KEY `idRecibo` (`idRecibo`),
  KEY `idPeriodo` (`idPeriodo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

COMMIT;
