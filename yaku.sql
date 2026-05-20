# Host: localhost  (Version 5.7.42-log)
# Date: 2026-05-19 21:27:43
# Generator: MySQL-Front 5.4  (Build 1.8)

/*!40101 SET NAMES latin1 */;

#
# Structure for table "abrirstock"
#

CREATE TABLE `abrirstock` (
  `llave` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  `turno` varchar(11) DEFAULT NULL,
  `caja` int(11) DEFAULT NULL,
  `producto` int(11) DEFAULT NULL,
  `cantidad` double DEFAULT NULL,
  `notas` varchar(255) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `upduser` varchar(30) DEFAULT NULL,
  `upddate` varchar(30) DEFAULT NULL,
  `cerrado` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`llave`)
) ENGINE=InnoDB AUTO_INCREMENT=1082 DEFAULT CHARSET=latin1;

#
# Structure for table "asistencia"
#

CREATE TABLE `asistencia` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `dni` varchar(11) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `turno` varchar(11) DEFAULT NULL,
  `llaves` varchar(15) DEFAULT NULL,
  `encargos` varchar(50) DEFAULT NULL,
  `horaent` varchar(12) DEFAULT NULL,
  `horasal` varchar(12) DEFAULT NULL,
  `user` varchar(15) DEFAULT NULL,
  `Sauna` tinyint(1) DEFAULT NULL,
  `SALIDA` tinyint(1) DEFAULT NULL,
  `IMPORTE` double DEFAULT NULL,
  `UPDDATE` varchar(15) DEFAULT NULL,
  `UPDUSER` varchar(15) DEFAULT NULL,
  `UPDTYPE` int(11) DEFAULT NULL,
  `Notas` varchar(255) DEFAULT NULL,
  `horasauna` varchar(20) DEFAULT NULL,
  `ducha` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=73259 DEFAULT CHARSET=latin1;

#
# Structure for table "cerrarstock"
#

CREATE TABLE `cerrarstock` (
  `llave` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  `turno` varchar(11) DEFAULT NULL,
  `caja` int(11) DEFAULT NULL,
  `producto` int(11) DEFAULT NULL,
  `stockfisico` double DEFAULT NULL,
  `notas` varchar(255) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `upduser` varchar(30) DEFAULT NULL,
  `upddate` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`llave`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "cliente"
#

CREATE TABLE `cliente` (
  `CODIGO` varchar(20) NOT NULL,
  `NOMBRE` varchar(255) DEFAULT NULL,
  `DIRECCION` varchar(255) DEFAULT NULL,
  `TELEFONO` varchar(100) DEFAULT NULL,
  `NOTAS` mediumtext,
  `upddate` varchar(100) DEFAULT NULL,
  `upduser` varchar(100) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `rowid` int(11) DEFAULT NULL,
  `correo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODIGO`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

#
# Structure for table "cliente_copy"
#

CREATE TABLE `cliente_copy` (
  `CODIGO` varchar(20) DEFAULT NULL,
  `NOMBRE` varchar(255) DEFAULT NULL,
  `DIRECCION` varchar(255) DEFAULT NULL,
  `TELEFONO` varchar(100) DEFAULT NULL,
  `NOTAS` mediumtext,
  `upddate` varchar(100) DEFAULT NULL,
  `upduser` varchar(100) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "compdet"
#

CREATE TABLE `compdet` (
  `LLAVE` int(11) NOT NULL AUTO_INCREMENT,
  `COMPRA` int(11) DEFAULT NULL,
  `PRODUCTO` int(11) DEFAULT NULL,
  `CANTIDAD` int(11) DEFAULT NULL,
  `PRECIO` double DEFAULT NULL,
  `NOTAS` varchar(255) DEFAULT NULL,
  `UNIDAD` varchar(100) DEFAULT NULL,
  `EQUIVALE` int(11) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`LLAVE`)
) ENGINE=InnoDB AUTO_INCREMENT=3750 DEFAULT CHARSET=latin1;

#
# Structure for table "compra"
#

CREATE TABLE `compra` (
  `NUMERO` int(11) NOT NULL AUTO_INCREMENT,
  `FECHA` date DEFAULT NULL,
  `DOCUM` varchar(100) DEFAULT NULL,
  `NUMDOC` varchar(100) DEFAULT NULL,
  `PROVEEDOR` varchar(11) DEFAULT NULL,
  `IMPORTE` double DEFAULT NULL,
  `NOTAS` varchar(255) DEFAULT NULL,
  `MARCA` tinyint(1) DEFAULT NULL,
  `CREDITO` tinyint(1) DEFAULT NULL,
  `UPDDATE` varchar(100) DEFAULT NULL,
  `UPDUSER` varchar(100) DEFAULT NULL,
  `UPDTYPE` int(11) DEFAULT NULL,
  `LOCAL` int(11) DEFAULT NULL,
  PRIMARY KEY (`NUMERO`)
) ENGINE=InnoDB AUTO_INCREMENT=40246128 DEFAULT CHARSET=latin1;

#
# Structure for table "movimientos"
#

CREATE TABLE `movimientos` (
  `llave` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `user` int(11) DEFAULT NULL,
  `turno` varchar(11) DEFAULT NULL,
  `caja` int(11) DEFAULT NULL,
  `producto` int(11) DEFAULT NULL,
  `cantidad` double DEFAULT NULL,
  `notas` varchar(255) DEFAULT NULL,
  `hora` varchar(15) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `upduser` varchar(30) DEFAULT NULL,
  `upddate` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`llave`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "persona"
#

CREATE TABLE `persona` (
  `codigo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) DEFAULT NULL,
  `cargo` varchar(255) DEFAULT NULL,
  `upddate` varchar(50) DEFAULT NULL,
  `upduser` varchar(100) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=latin1;

#
# Structure for table "plan"
#

CREATE TABLE `plan` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `nplan` varchar(200) DEFAULT NULL,
  `dsauna` varchar(5) DEFAULT NULL,
  `nsauna` int(11) DEFAULT NULL,
  `precio` double DEFAULT NULL,
  `observa` varchar(255) DEFAULT NULL,
  `UPDDATE` varchar(30) DEFAULT NULL,
  `UPDUSER` varchar(30) DEFAULT NULL,
  `UPDTYPE` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=latin1;

#
# Structure for table "producto"
#

CREATE TABLE `producto` (
  `CODIGO` int(11) NOT NULL AUTO_INCREMENT,
  `NOMBRE` varchar(255) DEFAULT NULL,
  `CODIGO2` varchar(50) DEFAULT NULL,
  `MARCA` varchar(50) DEFAULT NULL,
  `PRECIO` double DEFAULT NULL,
  `STOCK` int(11) DEFAULT NULL,
  `NOTAS` varchar(255) DEFAULT NULL,
  `CSOLES` double DEFAULT NULL,
  `PCAJA` double DEFAULT NULL,
  `UXCAJA` double DEFAULT NULL,
  `PUND` double DEFAULT NULL,
  `PDOC` double DEFAULT NULL,
  `UBICACION` varchar(50) DEFAULT NULL,
  `PAQUETE` varchar(50) DEFAULT NULL,
  `upddate` varchar(100) DEFAULT NULL,
  `upduser` varchar(100) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `INICIAL` double DEFAULT NULL,
  `BARRAS` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`CODIGO`)
) ENGINE=InnoDB AUTO_INCREMENT=2060 DEFAULT CHARSET=latin1;

#
# Structure for table "proveedor"
#

CREATE TABLE `proveedor` (
  `CODIGO` varchar(11) NOT NULL DEFAULT '',
  `NOMBRE` varchar(255) DEFAULT NULL,
  `TELEFONO` varchar(100) DEFAULT NULL,
  `DIRECCION` varchar(255) DEFAULT NULL,
  `NOTAS` varchar(255) DEFAULT NULL,
  `UPDDATE` varchar(100) DEFAULT NULL,
  `UPDTYPE` int(11) DEFAULT NULL,
  `UPDUSER` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`CODIGO`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

#
# Structure for table "socio"
#

CREATE TABLE `socio` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `dni` varchar(11) DEFAULT NULL,
  `plan` int(11) DEFAULT NULL,
  `desde` date DEFAULT NULL,
  `hasta` date DEFAULT NULL,
  `notas` varchar(255) DEFAULT NULL,
  `fecnac` date DEFAULT NULL,
  `sexo` varchar(1) DEFAULT NULL,
  `UPDUSER` varchar(30) DEFAULT NULL,
  `UPDDATE` varchar(20) DEFAULT NULL,
  `UPDTYPE` int(11) DEFAULT NULL,
  `fecreg` date DEFAULT NULL,
  `Persona` int(11) DEFAULT NULL,
  `DEBE` double DEFAULT NULL,
  `CONTRATO` varchar(100) DEFAULT NULL,
  `FONO` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=2177 DEFAULT CHARSET=latin1;

#
# Structure for table "tcontract"
#

CREATE TABLE `tcontract` (
  `Idcontract` int(11) NOT NULL AUTO_INCREMENT,
  `ccode` varchar(255) DEFAULT NULL,
  `cdescription` varchar(255) DEFAULT NULL,
  `contractor` int(11) DEFAULT NULL,
  `ctype` int(11) DEFAULT NULL,
  `cnotes` mediumtext,
  `cawarddate` date DEFAULT NULL,
  `currency` int(11) DEFAULT NULL,
  `closed` tinyint(1) DEFAULT NULL,
  `cresponsible` int(11) DEFAULT NULL,
  `fsnumber` varchar(100) DEFAULT NULL,
  `cnumber` varchar(50) DEFAULT NULL,
  `deliverydate` date DEFAULT NULL,
  `ccer` int(11) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `mstart` int(11) DEFAULT NULL,
  `mfinish` int(11) DEFAULT NULL,
  `mcurvetype` varchar(1) DEFAULT NULL,
  `cpayterms` int(11) DEFAULT NULL COMMENT 'Terminos de pago en nro de dias',
  PRIMARY KEY (`Idcontract`),
  KEY `fcer` (`ccer`),
  KEY `fcode` (`ccode`),
  KEY `fcontractor` (`contractor`),
  KEY `fcurrency` (`currency`),
  KEY `fresponsible` (`cresponsible`),
  KEY `ftype` (`ctype`),
  KEY `fupdtype` (`updtype`)
) ENGINE=InnoDB AUTO_INCREMENT=3257 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "tcontractor"
#

CREATE TABLE `tcontractor` (
  `Idcontractor` int(11) NOT NULL AUTO_INCREMENT,
  `namecontractor` varchar(255) DEFAULT NULL,
  `codecontractor` varchar(50) DEFAULT NULL,
  `caddress1` varchar(255) DEFAULT NULL,
  `caddress2` varchar(255) DEFAULT NULL,
  `caddress3` varchar(255) DEFAULT NULL,
  `ccity` varchar(100) DEFAULT NULL,
  `cstate` varchar(100) DEFAULT NULL,
  `ccountry` varchar(100) DEFAULT NULL,
  `cpostcode` varchar(100) DEFAULT NULL,
  `ccontact` varchar(255) DEFAULT NULL,
  `cphone` varchar(100) DEFAULT NULL,
  `cemail` varchar(255) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`Idcontractor`),
  KEY `fcodecontractor` (`codecontractor`),
  KEY `fupdtype` (`updtype`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "tperiod"
#

CREATE TABLE `tperiod` (
  `Idperiod` int(11) NOT NULL AUTO_INCREMENT,
  `pnumber` int(11) DEFAULT NULL,
  `pname1` varchar(50) DEFAULT NULL,
  `pname2` varchar(50) DEFAULT NULL,
  `pactive` tinyint(1) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `dateend` date DEFAULT NULL,
  PRIMARY KEY (`Idperiod`),
  KEY `kactive` (`pactive`),
  KEY `kname1` (`pname1`),
  KEY `knumber` (`pnumber`),
  KEY `kupdtype` (`updtype`)
) ENGINE=InnoDB AUTO_INCREMENT=455 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "venta"
#

CREATE TABLE `venta` (
  `NUMERO` int(11) NOT NULL AUTO_INCREMENT,
  `FECHA` datetime DEFAULT NULL,
  `DOCUM` varchar(20) DEFAULT NULL,
  `NUMDOC` int(11) DEFAULT NULL,
  `CLIENTE` varchar(20) DEFAULT NULL,
  `IMPORTE` double DEFAULT NULL,
  `NOTAS` varchar(255) DEFAULT NULL,
  `MARCA` tinyint(1) DEFAULT NULL,
  `ANULA` tinyint(1) DEFAULT NULL,
  `CREDITO` tinyint(1) DEFAULT NULL,
  `NNCLIENTE` varchar(255) DEFAULT NULL,
  `COSAS` varchar(255) DEFAULT NULL,
  `ACCESORIOS` varchar(255) DEFAULT NULL,
  `DEJA` double DEFAULT NULL,
  `REFERE` varchar(255) DEFAULT NULL,
  `CANCELADO` tinyint(1) DEFAULT NULL,
  `HORA` varchar(20) DEFAULT NULL,
  `TURNO` varchar(15) DEFAULT NULL,
  `HORASAL` varchar(20) DEFAULT NULL,
  `OBSERVA` varchar(255) DEFAULT NULL,
  `CAJA` int(11) DEFAULT NULL,
  `ESTADO` varchar(100) DEFAULT NULL,
  `upduser` varchar(100) DEFAULT NULL,
  `upddate` varchar(100) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `NRO` int(11) DEFAULT NULL,
  PRIMARY KEY (`NUMERO`)
) ENGINE=InnoDB AUTO_INCREMENT=125087 DEFAULT CHARSET=latin1;

#
# Structure for table "venta_copy"
#

CREATE TABLE `venta_copy` (
  `NUMERO` int(11) NOT NULL AUTO_INCREMENT,
  `FECHA` datetime DEFAULT NULL,
  `DOCUM` varchar(20) DEFAULT NULL,
  `NUMDOC` int(11) DEFAULT NULL,
  `CLIENTE` varchar(20) DEFAULT NULL,
  `IMPORTE` double DEFAULT NULL,
  `NOTAS` varchar(255) DEFAULT NULL,
  `MARCA` tinyint(1) DEFAULT NULL,
  `ANULA` tinyint(1) DEFAULT NULL,
  `CREDITO` tinyint(1) DEFAULT NULL,
  `NNCLIENTE` varchar(255) DEFAULT NULL,
  `COSAS` varchar(255) DEFAULT NULL,
  `ACCESORIOS` varchar(255) DEFAULT NULL,
  `DEJA` double DEFAULT NULL,
  `REFERE` varchar(255) DEFAULT NULL,
  `CANCELADO` tinyint(1) DEFAULT NULL,
  `HORA` varchar(20) DEFAULT NULL,
  `TURNO` varchar(15) DEFAULT NULL,
  `HORASAL` varchar(20) DEFAULT NULL,
  `OBSERVA` varchar(255) DEFAULT NULL,
  `CAJA` int(11) DEFAULT NULL,
  `ESTADO` varchar(100) DEFAULT NULL,
  `upduser` varchar(100) DEFAULT NULL,
  `upddate` varchar(100) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `NRO` int(11) DEFAULT NULL,
  PRIMARY KEY (`NUMERO`)
) ENGINE=InnoDB AUTO_INCREMENT=35050 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "ventadet"
#

CREATE TABLE `ventadet` (
  `LLAVE` int(11) NOT NULL AUTO_INCREMENT,
  `VENTA` int(11) DEFAULT NULL,
  `PRODUCTO` int(11) DEFAULT NULL,
  `CANTIDAD` double DEFAULT NULL,
  `PRECIO` double DEFAULT NULL,
  `NOTAS` varchar(255) DEFAULT NULL,
  `UNIDAD` varchar(30) DEFAULT NULL,
  `EQUIVALE` int(11) DEFAULT NULL,
  `PERSONA` varchar(255) DEFAULT NULL,
  `ATENDIDO` tinyint(1) DEFAULT NULL,
  `upddate` varchar(100) DEFAULT NULL,
  `upduser` varchar(100) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `ventan` int(11) DEFAULT NULL,
  PRIMARY KEY (`LLAVE`),
  KEY `producto` (`PRODUCTO`)
) ENGINE=InnoDB AUTO_INCREMENT=438522 DEFAULT CHARSET=latin1;

#
# Structure for table "xaudit"
#

CREATE TABLE `xaudit` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `vgrid` int(11) DEFAULT NULL,
  `idtable` int(11) DEFAULT NULL,
  `vtype` int(11) DEFAULT NULL COMMENT 'insert, update, delete',
  `vdate` date DEFAULT NULL,
  `vtime` varchar(20) DEFAULT NULL,
  `vuser` int(11) DEFAULT NULL,
  `vvalue` longtext,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xconsults"
#

CREATE TABLE `xconsults` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) DEFAULT NULL,
  `ssql` mediumtext,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=latin1;

#
# Structure for table "xcontrols"
#

CREATE TABLE `xcontrols` (
  `Idcontrol` int(11) NOT NULL AUTO_INCREMENT,
  `idform` int(11) DEFAULT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `texto` varchar(500) DEFAULT '',
  `codigo1` longtext,
  `codigo2` longtext,
  `donde` varchar(50) DEFAULT NULL,
  `alinear` int(11) DEFAULT NULL COMMENT '1.|alNone, alTop, alBottom, alLeft, alRight, alClient, alCustom);',
  `ancho` int(11) DEFAULT NULL,
  `memo` longtext COMMENT 'el memo recibe el menuitems, para caso de botones y arboles, codigo en codigo2',
  `icon` int(11) DEFAULT NULL,
  `Result` tinyint(1) DEFAULT NULL,
  `xdataset` varchar(100) DEFAULT NULL,
  `datafield` varchar(100) DEFAULT NULL,
  `listfield` varchar(100) DEFAULT NULL,
  `listformat` varchar(100) DEFAULT NULL,
  `nrocontrol` int(11) DEFAULT NULL,
  `FPOS` int(11) DEFAULT NULL COMMENT 'Para mantener la posicion de controles al copiar',
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `ocultartxt` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`Idcontrol`)
) ENGINE=InnoDB AUTO_INCREMENT=425 DEFAULT CHARSET=latin1;

#
# Structure for table "xfield"
#

CREATE TABLE `xfield` (
  `idf` int(11) NOT NULL AUTO_INCREMENT,
  `grid` int(11) DEFAULT NULL,
  `creaSQL` tinyint(1) DEFAULT NULL,
  `campo` varchar(70) DEFAULT NULL,
  `titlefield` varchar(150) DEFAULT NULL,
  `Cabeza` varchar(100) DEFAULT NULL,
  `Ayuda` varchar(255) DEFAULT NULL,
  `color` varchar(10) DEFAULT NULL,
  `fontcolor` varchar(10) DEFAULT NULL,
  `fontbold` tinyint(1) DEFAULT NULL,
  `alinear` varchar(1) DEFAULT NULL,
  `tipod` varchar(1) DEFAULT NULL,
  `formato` varchar(50) DEFAULT NULL,
  `valxdefecto` varchar(255) DEFAULT '',
  `valcombo` mediumtext,
  `datafield` varchar(50) DEFAULT NULL,
  `oculto` tinyint(1) DEFAULT NULL,
  `eoculto` tinyint(1) DEFAULT NULL,
  `readonly` tinyint(1) DEFAULT NULL,
  `TipoMemo` int(11) DEFAULT NULL COMMENT 'memo: 1 simple, 2 html, 3 pascal',
  `totalizar` tinyint(1) DEFAULT NULL,
  `SValida` mediumtext,
  `ancho` int(11) DEFAULT NULL COMMENT 'por defecto',
  `posicion` int(11) DEFAULT NULL COMMENT 'por defecto',
  `Sortable` tinyint(1) DEFAULT NULL,
  `verMemo` tinyint(1) DEFAULT NULL,
  `vertooltip` tinyint(1) DEFAULT NULL,
  `calculado` tinyint(1) DEFAULT NULL,
  `locked` tinyint(1) DEFAULT NULL,
  `noanymatch` tinyint(1) DEFAULT NULL,
  `fieldorigen` varchar(255) DEFAULT NULL COMMENT 'nombre del campo field en el origen (para poder importar automat)',
  `listfield` varchar(100) DEFAULT NULL COMMENT 'lista de campos a mostrar separado por comas',
  `listformat` varchar(50) DEFAULT NULL COMMENT '(%s)-%s',
  `xdataset` varchar(50) DEFAULT NULL COMMENT 'Nombre "X" del clientdataset que esta en Mainmoudule',
  `NoFilter` tinyint(1) DEFAULT NULL,
  `obligatorio` tinyint(1) DEFAULT NULL,
  `salta` tinyint(1) DEFAULT NULL,
  `sqlcombo` mediumtext,
  `f9` mediumtext,
  `Agregar` tinyint(1) DEFAULT NULL COMMENT 'Use para mostrar "+" en el combo y agregar desde el EDITOR',
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `noimport` tinyint(1) DEFAULT NULL COMMENT 'si esta marcado ese campo no lo envia al export ni al import',
  `vunique` tinyint(1) DEFAULT NULL COMMENT 'para indicar si el CODE (o cualquier otro campo) es unico en el sistema.',
  `fcalcula` varchar(255) DEFAULT NULL,
  `ocultarmobil` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`idf`)
) ENGINE=InnoDB AUTO_INCREMENT=6875 DEFAULT CHARSET=latin1;

#
# Structure for table "xfiltro"
#

CREATE TABLE `xfiltro` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `vuser` int(11) DEFAULT NULL,
  `vform` int(11) DEFAULT NULL,
  `vfield` varchar(255) DEFAULT NULL,
  `voperator` varchar(50) DEFAULT NULL,
  `vvalue` varchar(255) DEFAULT NULL,
  `vconector` varchar(20) DEFAULT NULL,
  `vcampo` varchar(255) DEFAULT NULL,
  `vtipo` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xforms"
#

CREATE TABLE `xforms` (
  `Idform` int(11) NOT NULL AUTO_INCREMENT,
  `cform` varchar(100) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT '' COMMENT 'Se puede utilizar para la ayuda de ese grid de datos',
  `tipo` int(11) DEFAULT NULL,
  `parent` int(11) DEFAULT NULL,
  `iconform` int(11) DEFAULT NULL,
  `Screate` longtext,
  `SActivate` longtext,
  `NroPaneles` int(11) DEFAULT NULL,
  `distribucion` varchar(4) DEFAULT NULL COMMENT 'AAAA, AABB, ABAB, AABC...',
  `enlace` varchar(255) DEFAULT NULL,
  `FormHeader` longtext,
  `FormFooter` longtext,
  `FormHeaderUni` longtext,
  `FormFooterUni` longtext,
  `FormHeadermovil` longtext,
  `FormFooterMovil` longtext,
  `FormHeaderMovilUni` longtext,
  `FormFooterMovilUni` longtext,
  `HeaderAlto` int(11) DEFAULT NULL,
  `FooterAlto` int(11) DEFAULT NULL,
  `fwidth` int(11) DEFAULT NULL,
  `fheight` int(11) DEFAULT NULL,
  `fmax` tinyint(1) DEFAULT NULL,
  `nroform` int(11) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `Simport` longtext,
  `Sexport` longtext,
  `Sclose` longtext,
  PRIMARY KEY (`Idform`)
) ENGINE=InnoDB AUTO_INCREMENT=283 DEFAULT CHARSET=latin1;

#
# Structure for table "xfunctions"
#

CREATE TABLE `xfunctions` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `funcion` varchar(50) DEFAULT NULL,
  `scode` longtext,
  `updtype` int(11) DEFAULT NULL,
  `upddate` varchar(20) DEFAULT NULL,
  `upduser` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xgrid"
#

CREATE TABLE `xgrid` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) DEFAULT NULL,
  `mayusculas` tinyint(1) DEFAULT NULL,
  `recnoedit` tinyint(1) DEFAULT NULL COMMENT 'Editor de datos formulario',
  `insertSQL` mediumtext,
  `updateSQL` mediumtext,
  `deleteSQL` mediumtext,
  `refreshSQL` mediumtext,
  `ocultabar` tinyint(1) DEFAULT NULL COMMENT 'Oculta la barra de herram. agregar, borrar, etc.',
  `readonlyg` tinyint(1) DEFAULT NULL,
  `AltoFila` int(11) DEFAULT NULL,
  `fieldmark` varchar(50) DEFAULT NULL COMMENT 'marcar para no editar',
  `Anchofe` int(11) DEFAULT NULL COMMENT 'Se usa para el taman',
  `Altofe` int(11) DEFAULT NULL COMMENT 'Se usa para el form.edicion',
  `rxpage` int(11) DEFAULT NULL,
  `VQUERY` varchar(50) DEFAULT NULL COMMENT 'SOLO NOMBRE DEL QUERY',
  `ocultafilter` tinyint(1) DEFAULT NULL,
  `colorhelp` int(11) DEFAULT NULL,
  `AnchoT` int(11) DEFAULT NULL COMMENT 'ancho del titulo defecto 100',
  `seleccionar` tinyint(1) DEFAULT NULL COMMENT 'Se usa para que muestre el grid con selection',
  `nroframe` int(11) DEFAULT NULL,
  `SDelete` longtext,
  `SDeletePost` longtext,
  `Sinsert` longtext,
  `Sopen` longtext,
  `Snewrecord` longtext,
  `Sscroll` longtext,
  `Scalcula` longtext,
  `xform` int(11) DEFAULT NULL,
  `titulo` varchar(255) DEFAULT NULL,
  `menuitems` mediumtext,
  `Smenuitem` longtext,
  `Formblank` longtext,
  `FormBlankMovil` longtext,
  `FormBlankUni` longtext,
  `FormBlankMovilUni` longtext,
  `FieldGroup` varchar(100) DEFAULT NULL,
  `Ssave` longtext,
  `ssavepost` longtext,
  `sedit` longtext,
  `FPOS` int(11) DEFAULT NULL,
  `nrogrid` int(11) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `sdraw` mediumtext,
  `porcentaje` int(11) DEFAULT NULL,
  `intab` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=691 DEFAULT CHARSET=latin1;

#
# Structure for table "xicons"
#

CREATE TABLE `xicons` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `fuente` int(11) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `nroicon` int(11) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xidioma"
#

CREATE TABLE `xidioma` (
  `Ididioma` int(11) NOT NULL AUTO_INCREMENT,
  `idiomadesc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Ididioma`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xidiomadest"
#

CREATE TABLE `xidiomadest` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Caption1` varchar(255) DEFAULT NULL,
  `Caption2` varchar(255) DEFAULT NULL,
  `Caption3` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xidiomaori"
#

CREATE TABLE `xidiomaori` (
  `Ididiomaori` int(11) NOT NULL AUTO_INCREMENT,
  `Caption1` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Ididiomaori`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "ximporterror"
#

CREATE TABLE `ximporterror` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `cRow` int(11) DEFAULT NULL,
  `cColumn` int(11) DEFAULT NULL,
  `Comments` varchar(255) DEFAULT NULL,
  `ctable` varchar(100) DEFAULT NULL,
  `ctype` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=133102 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xmsg"
#

CREATE TABLE `xmsg` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `message` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=350 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xreportcond"
#

CREATE TABLE `xreportcond` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `reportespec` int(11) DEFAULT NULL COMMENT 'Para filtro especifico (guardado por user)',
  `abrepar` varchar(5) DEFAULT NULL,
  `ncampo` varchar(100) DEFAULT NULL,
  `operador` varchar(30) DEFAULT NULL,
  `valor1` varchar(255) DEFAULT NULL,
  `valor2` varchar(255) DEFAULT NULL,
  `cierrapar` varchar(5) DEFAULT NULL,
  `conector` varchar(5) DEFAULT NULL,
  `report` int(11) DEFAULT NULL COMMENT 'Para filtro solo del reporte',
  `nfield` varchar(100) DEFAULT NULL,
  `ntype` varchar(1) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xreportespec"
#

CREATE TABLE `xreportespec` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `reporte` int(11) DEFAULT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `usuario` int(11) DEFAULT NULL,
  `global` tinyint(1) DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xreportfilter"
#

CREATE TABLE `xreportfilter` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Idreport` int(11) DEFAULT NULL COMMENT 'En realidad es el TIPO DE REPORTE (Un campo en los reportes)',
  `cfield` varchar(50) DEFAULT NULL COMMENT 'con este nombre de campo se arma la condicion',
  `ctitle` varchar(50) DEFAULT NULL COMMENT 'este nombre se muestra en el desplegable',
  `ctype` varchar(5) DEFAULT NULL COMMENT 'F, N, L, C (para ver si es Lista, fecha, etc)',
  `CValues` mediumtext COMMENT 'valores para un combo, ejm. sexo, turno, etc.',
  `xquery` varchar(255) DEFAULT NULL COMMENT 'Ejm: Select  reccode as code, recname1 as name from tresource',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xreportgroup"
#

CREATE TABLE `xreportgroup` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `report` int(11) DEFAULT NULL,
  `titulo` varchar(100) DEFAULT NULL,
  `campo` varchar(100) DEFAULT NULL,
  `isdefined` tinyint(1) DEFAULT NULL COMMENT 'is defined field?. codificar desde el framework',
  `ncampo` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xreports"
#

CREATE TABLE `xreports` (
  `Id` int(11) NOT NULL DEFAULT '0',
  `number` int(11) DEFAULT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `parent` int(11) DEFAULT NULL,
  `nreport` varchar(255) DEFAULT NULL,
  `imageindex` int(11) DEFAULT NULL,
  `disabled` int(11) DEFAULT NULL,
  `codigo` longtext,
  `Title` varchar(255) DEFAULT NULL,
  `consulta` mediumtext,
  `grid` int(11) DEFAULT NULL COMMENT 'se relaciona con el grid de los t',
  `Rformato` longtext,
  `tipo` int(11) DEFAULT NULL COMMENT 'Tipo de reporte para enlazar con los filtros (en idreport)'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

#
# Structure for table "xrol"
#

CREATE TABLE `xrol` (
  `IdRol` int(11) NOT NULL AUTO_INCREMENT,
  `RolName` varchar(100) DEFAULT NULL,
  `Description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`IdRol`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xrolxform"
#

CREATE TABLE `xrolxform` (
  `Idrolxform` int(11) NOT NULL AUTO_INCREMENT,
  `idform` int(11) DEFAULT NULL,
  `idrol` int(11) DEFAULT NULL,
  `nread` tinyint(1) DEFAULT NULL,
  `nwrite` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`Idrolxform`)
) ENGINE=InnoDB AUTO_INCREMENT=489 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xsistema"
#

CREATE TABLE `xsistema` (
  `Id` int(11) NOT NULL DEFAULT '0',
  `title` varchar(255) DEFAULT NULL,
  `code` longtext,
  `icondev` int(11) DEFAULT NULL,
  `icondef` int(11) DEFAULT NULL,
  `iconman` int(11) DEFAULT NULL,
  `iconrep` int(11) DEFAULT NULL,
  `iconcon` int(11) DEFAULT NULL,
  `iconsys` int(11) DEFAULT NULL,
  `tipomenu` int(11) DEFAULT NULL COMMENT '0: todos, 1. arriba, 2. izquierda',
  `xsqls` mediumtext,
  `SinLogin` tinyint(1) DEFAULT NULL COMMENT 'indica si se ingresa sinloguearse al sistema',
  `IdiomaDefault` int(11) DEFAULT NULL COMMENT 'Idioma por defecto',
  `SActivate` longtext,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `NoAuditar` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

#
# Structure for table "xuser"
#

CREATE TABLE `xuser` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `nuser` varchar(100) DEFAULT NULL,
  `tipo` int(11) DEFAULT NULL COMMENT 'Admin, worker, responsibility, vendor',
  `password` varchar(50) DEFAULT NULL,
  `contractor` int(11) DEFAULT NULL,
  `ChangePw` tinyint(1) DEFAULT NULL,
  `name` varchar(80) DEFAULT NULL,
  `modules` varchar(255) DEFAULT NULL,
  `modulesno` varchar(255) DEFAULT NULL,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  `Rol` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=226 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xuserlog"
#

CREATE TABLE `xuserlog` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `iduser` int(11) DEFAULT NULL,
  `vdate` date DEFAULT NULL,
  `vtime` varchar(15) DEFAULT NULL,
  `Action` varchar(255) DEFAULT NULL COMMENT 'ingreso, click modulo, reporte',
  `Modulos` mediumtext,
  `upduser` varchar(50) DEFAULT NULL,
  `upddate` varchar(25) DEFAULT NULL,
  `updtype` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=18739 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# Structure for table "xwall"
#

CREATE TABLE `xwall` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `numero` int(11) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;

#
# View "qabrirstock"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qabrirstock`
    AS
      SELECT
        `abrirstock`.`llave`,
        `abrirstock`.`fecha`,
        `abrirstock`.`user`,
        `abrirstock`.`turno`,
        `abrirstock`.`caja`,
        `abrirstock`.`producto`,
        `abrirstock`.`cantidad`,
        `abrirstock`.`notas`,
        `abrirstock`.`updtype`,
        `abrirstock`.`upduser`,
        `abrirstock`.`upddate`,
        `abrirstock`.`cerrado`,
        `producto`.`NOMBRE` AS `nombre`
      FROM
        (`abrirstock` 
          LEFT JOIN `producto` ON ((`abrirstock`.`producto` = `producto`.`CODIGO`)));

#
# View "qasistencia"
#

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `qasistencia` AS SELECT
  `asistencia`.`Id`,
  `asistencia`.`dni`,
  `asistencia`.`fecha`,
  `asistencia`.`turno`,
  `asistencia`.`llaves`,
  `asistencia`.`encargos`,
  `asistencia`.`horaent`,
  `asistencia`.`horasal`,
  `asistencia`.`user`,
  `asistencia`.`Sauna`,
  `asistencia`.`SALIDA`,
  `asistencia`.`IMPORTE`,
  `asistencia`.`UPDDATE`,
  `asistencia`.`UPDUSER`,
  `asistencia`.`UPDTYPE`,
  `asistencia`.`Notas`,
  `asistencia`.`horasauna`,
  `asistencia`.`ducha`,
  `cliente`.`NOMBRE`,
  `socio`.`plan`,
  `socio`.`desde`,
  `socio`.`hasta`,
  `socio`.`fecnac`,
  `socio`.`sexo`,
  CONVERT(CAST(((YEAR(CURDATE()) - YEAR(`socio`.`fecnac`)) - (DATE_FORMAT(CURDATE(), '%m%d') < DATE_FORMAT(`socio`.`fecnac`, '%m%d'))) AS char CHARSET utf8 CHARSET utf8) USING latin1) AS `edad`,
  `plan`.`nplan`,
  `plan`.`nsauna`,
  `plan`.`precio`,
  CONVERT(TIME_FORMAT(TIMEDIFF(IF(`asistencia`.`SALIDA`, CAST(`asistencia`.`horasal` AS time(6)), CAST(NOW() AS time)), CAST(`asistencia`.`horasauna` AS time(6))), '%H:%i:%s') USING latin1) AS `TIEMPOSAUNA`
FROM
  (((`asistencia` 
    LEFT JOIN `cliente` ON ((`asistencia`.`dni` = `cliente`.`CODIGO`))) 
    LEFT JOIN `socio` ON ((`cliente`.`CODIGO` = `socio`.`dni`))) 
    LEFT JOIN `plan` ON ((`socio`.`plan` = `plan`.`Id`)))
#
# View "qaudit"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qaudit`
    AS
      SELECT
        `xaudit`.`Id`,
        `xaudit`.`vgrid`,
        `xaudit`.`idtable`,
        `xaudit`.`vtype`,
        `xaudit`.`vdate`,
        `xaudit`.`vtime`,
        `xaudit`.`vuser`,
        `xaudit`.`vvalue`,
        `xaudit`.`upduser`,
        `xaudit`.`upddate`,
        `xaudit`.`updtype`,
        `xgrid`.`nombre`,
        `xforms`.`cform`,
        `xuser`.`nuser`,
        `xgrid`.`titulo`,
        `xforms`.`descripcion`
      FROM
        (((`xaudit` 
          JOIN `xuser` ON ((`xuser`.`Id` = `xaudit`.`vuser`))) 
          JOIN `xgrid` ON ((`xgrid`.`Id` = `xaudit`.`vgrid`))) 
          JOIN `xforms` ON ((`xforms`.`Idform` = `xgrid`.`xform`)));

#
# View "qcompra"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qcompra`
    AS
      SELECT
        `compra`.`NUMERO`,
        `compra`.`FECHA`,
        `compra`.`DOCUM`,
        `compra`.`NUMDOC`,
        `compra`.`PROVEEDOR`,
        `compra`.`IMPORTE`,
        `compra`.`NOTAS`,
        `compra`.`MARCA`,
        `compra`.`CREDITO`,
        `compra`.`UPDDATE`,
        `compra`.`UPDUSER`,
        `compra`.`UPDTYPE`,
        `proveedor`.`NOMBRE`
      FROM
        (`compra` 
          LEFT JOIN `proveedor` ON ((`compra`.`PROVEEDOR` = `proveedor`.`CODIGO`)));

#
# View "qcompdet"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qcompdet`
    AS
      SELECT
        `compdet`.`LLAVE`,
        `compdet`.`COMPRA`,
        `compdet`.`PRODUCTO`,
        `compdet`.`CANTIDAD`,
        `compdet`.`PRECIO`,
        `compdet`.`NOTAS`,
        `compdet`.`UNIDAD`,
        `compdet`.`EQUIVALE`,
        `compdet`.`upduser`,
        `compdet`.`upddate`,
        `compdet`.`updtype`,
        `producto`.`NOMBRE` AS `nombre`,
        `qcompra`.`NOMBRE` AS `npersona`,
        `qcompra`.`FECHA` AS `fecha`,
        `qcompra`.`NUMDOC` AS `refere`
      FROM
        ((`compdet` 
          LEFT JOIN `producto` ON ((`producto`.`CODIGO` = `compdet`.`PRODUCTO`))) 
          LEFT JOIN `qcompra` ON ((`qcompra`.`NUMERO` = `compdet`.`COMPRA`)));

#
# View "qmovimientos"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qmovimientos`
    AS
      SELECT
        `movimientos`.`llave`,
        `movimientos`.`fecha`,
        `movimientos`.`user`,
        `movimientos`.`turno`,
        `movimientos`.`caja`,
        `movimientos`.`producto`,
        `movimientos`.`cantidad`,
        `movimientos`.`notas`,
        `movimientos`.`hora`,
        `movimientos`.`updtype`,
        `movimientos`.`upduser`,
        `movimientos`.`upddate`,
        `producto`.`NOMBRE` AS `nombre`
      FROM
        (`movimientos` 
          LEFT JOIN `producto` ON ((`movimientos`.`producto` = `producto`.`CODIGO`)));

#
# View "qsocio"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qsocio`
    AS
      SELECT
        `cliente`.`NOMBRE`,
        `plan`.`nplan`,
        `socio`.`Id`,
        `socio`.`dni`,
        `socio`.`plan`,
        `socio`.`desde`,
        `socio`.`hasta`,
        `socio`.`notas`,
        `socio`.`fecnac`,
        `socio`.`sexo`,
        `socio`.`UPDUSER`,
        `socio`.`UPDDATE`,
        `socio`.`UPDTYPE`,
        `socio`.`fecreg`,
        `socio`.`Persona`,
        `socio`.`DEBE`,
        `socio`.`CONTRATO`,
        `socio`.`FONO`,
        `cliente`.`DIRECCION`,
        `cliente`.`TELEFONO`,
        `plan`.`dsauna`,
        `plan`.`nsauna`,
        `plan`.`precio`,
        `plan`.`observa`,
        `persona`.`nombre` AS `npersona`
      FROM
        (((`socio` 
          LEFT JOIN `plan` ON ((`plan`.`Id` = `socio`.`plan`))) 
          LEFT JOIN `cliente` ON ((`cliente`.`CODIGO` = `socio`.`dni`))) 
          LEFT JOIN `persona` ON ((`persona`.`codigo` = `socio`.`Persona`)));

#
# View "quser"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `quser`
    AS
      SELECT
        `xuser`.`Id`,
        `xuser`.`nuser`,
        `xuser`.`tipo`,
        `xuser`.`password`,
        `xuser`.`contractor`,
        `xuser`.`ChangePw`,
        `xuser`.`name`,
        `xuser`.`modules`,
        `xuser`.`modulesno`,
        `xuser`.`upduser`,
        `xuser`.`upddate`,
        `xuser`.`updtype`,
        `xuser`.`Rol`,
        `tcontractor`.`namecontractor` AS `NAMECONTRACTOR`
      FROM
        (`xuser` 
          LEFT JOIN `tcontractor` ON ((`tcontractor`.`Idcontractor` = `xuser`.`contractor`)));

#
# View "quserlog"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `quserlog`
    AS
      SELECT
        `xuser`.`name`,
        `xuser`.`nuser`,
        `xuserlog`.`Id`,
        `xuserlog`.`iduser`,
        `xuserlog`.`vdate`,
        `xuserlog`.`vtime`,
        `xuserlog`.`Action`,
        `xuserlog`.`Modulos`,
        `xuserlog`.`upduser`,
        `xuserlog`.`upddate`,
        `xuserlog`.`updtype`
      FROM
        (`xuserlog` 
          LEFT JOIN `xuser` ON ((`xuser`.`Id` = `xuserlog`.`iduser`)));

#
# View "qventa"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qventa`
    AS
      SELECT
        `venta`.`NUMERO`,
        `venta`.`FECHA`,
        `venta`.`DOCUM`,
        `venta`.`NUMDOC`,
        `venta`.`CLIENTE`,
        `venta`.`IMPORTE`,
        `venta`.`NOTAS`,
        `venta`.`MARCA`,
        `venta`.`ANULA`,
        `venta`.`CREDITO`,
        `venta`.`NNCLIENTE`,
        `venta`.`COSAS`,
        `venta`.`ACCESORIOS`,
        `venta`.`DEJA`,
        `venta`.`REFERE`,
        `venta`.`CANCELADO`,
        `venta`.`HORA`,
        `venta`.`TURNO`,
        `venta`.`HORASAL`,
        `venta`.`OBSERVA`,
        `venta`.`CAJA`,
        `venta`.`ESTADO`,
        `venta`.`upduser`,
        `venta`.`upddate`,
        `venta`.`updtype`,
        `venta`.`NRO`,
        `cliente`.`DIRECCION` AS `direccion`
      FROM
        (`venta` 
          LEFT JOIN `cliente` ON ((`venta`.`CLIENTE` = `cliente`.`CODIGO`)));

#
# View "qventadet"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qventadet`
    AS
      SELECT
        `ventadet`.`LLAVE`,
        `ventadet`.`VENTA`,
        `ventadet`.`PRODUCTO`,
        `ventadet`.`CANTIDAD`,
        `ventadet`.`PRECIO`,
        `ventadet`.`NOTAS`,
        `ventadet`.`UNIDAD`,
        `ventadet`.`EQUIVALE`,
        `ventadet`.`PERSONA`,
        `ventadet`.`ATENDIDO`,
        `ventadet`.`upddate`,
        `ventadet`.`upduser`,
        `ventadet`.`updtype`,
        `ventadet`.`ventan`,
        `producto`.`NOMBRE` AS `nombre`,
        (`ventadet`.`CANTIDAD` * `ventadet`.`PRECIO`) AS `total`,
        `venta`.`NNCLIENTE` AS `npersona`,
        `venta`.`FECHA` AS `fecha`,
        `venta`.`NOTAS` AS `refere`
      FROM
        ((`ventadet` 
          LEFT JOIN `producto` ON ((`ventadet`.`PRODUCTO` = `producto`.`CODIGO`))) 
          LEFT JOIN `venta` ON ((`venta`.`NUMERO` = `ventadet`.`VENTA`)));

#
# View "qkardex"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qkardex`
    AS
      SELECT
        `qcompdet`.`PRODUCTO` AS `producto`,
        'Ingreso' AS `tipo`,
        `qcompdet`.`fecha`,
        `qcompdet`.`npersona`,
        `qcompdet`.`refere`,
        `qcompdet`.`CANTIDAD` AS `cantidad`,
        `qcompdet`.`PRECIO` AS `precio`,
        (`qcompdet`.`CANTIDAD` * `qcompdet`.`PRECIO`) AS `total`
      FROM
        `qcompdet`
      UNION
      SELECT
        `qventadet`.`PRODUCTO` AS `producto`,
        'Salida' AS `tipo`,
        `qventadet`.`fecha`,
        `qventadet`.`npersona`,
        `qventadet`.`refere`,
        `qventadet`.`CANTIDAD` AS `cantidad`,
        `qventadet`.`PRECIO` AS `precio`,
        (`qventadet`.`CANTIDAD` * `qventadet`.`PRECIO`) AS `total`
      FROM
        `qventadet`;

#
# View "qventadet2"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qventadet2`
    AS
      SELECT
        `ventadet`.`CANTIDAD`,
        `ventadet`.`PRODUCTO`,
        `ventadet`.`PRECIO`,
        `venta`.`FECHA`,
        `venta`.`CAJA`,
        `venta`.`TURNO`
      FROM
        (`ventadet` 
          JOIN `venta` ON ((`ventadet`.`VENTA` = `venta`.`NUMERO`)));

#
# View "qxgrid"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `qxgrid`
    AS
      SELECT
        `xgrid`.`Id`,
        `xgrid`.`nombre`,
        `xgrid`.`mayusculas`,
        `xgrid`.`recnoedit`,
        `xgrid`.`insertSQL`,
        `xgrid`.`updateSQL`,
        `xgrid`.`deleteSQL`,
        `xgrid`.`refreshSQL`,
        `xgrid`.`ocultabar`,
        `xgrid`.`readonlyg`,
        `xgrid`.`AltoFila`,
        `xgrid`.`fieldmark`,
        `xgrid`.`Anchofe`,
        `xgrid`.`Altofe`,
        `xgrid`.`rxpage`,
        `xgrid`.`VQUERY`,
        `xgrid`.`ocultafilter`,
        `xgrid`.`colorhelp`,
        `xgrid`.`AnchoT`,
        `xgrid`.`seleccionar`,
        `xgrid`.`nroframe`,
        `xgrid`.`SDelete`,
        `xgrid`.`SDeletePost`,
        `xgrid`.`Sinsert`,
        `xgrid`.`Sopen`,
        `xgrid`.`Snewrecord`,
        `xgrid`.`Sscroll`,
        `xgrid`.`Scalcula`,
        `xgrid`.`xform`,
        `xgrid`.`titulo`,
        `xgrid`.`menuitems`,
        `xgrid`.`Smenuitem`,
        `xgrid`.`Formblank`,
        `xgrid`.`FormBlankMovil`,
        `xgrid`.`FormBlankUni`,
        `xgrid`.`FormBlankMovilUni`,
        `xgrid`.`FieldGroup`,
        `xgrid`.`Ssave`,
        `xgrid`.`ssavepost`,
        `xgrid`.`sedit`,
        `xgrid`.`FPOS`,
        `xgrid`.`nrogrid`,
        `xgrid`.`upduser`,
        `xgrid`.`upddate`,
        `xgrid`.`updtype`,
        `xgrid`.`sdraw`,
        `xgrid`.`porcentaje`,
        `xgrid`.`intab`,
        `xforms`.`Idform`,
        `xforms`.`cform`,
        `xforms`.`descripcion`,
        `xforms`.`tipo`,
        `xforms`.`parent`,
        `xforms`.`iconform`,
        `xforms`.`Screate`,
        `xforms`.`SActivate`,
        `xforms`.`NroPaneles`,
        `xforms`.`distribucion`,
        `xforms`.`enlace`,
        `xforms`.`FormHeader`,
        `xforms`.`FormFooter`,
        `xforms`.`FormHeaderUni`,
        `xforms`.`FormFooterUni`,
        `xforms`.`FormHeadermovil`,
        `xforms`.`FormFooterMovil`,
        `xforms`.`FormHeaderMovilUni`,
        `xforms`.`FormFooterMovilUni`,
        `xforms`.`HeaderAlto`,
        `xforms`.`FooterAlto`,
        `xforms`.`fwidth`,
        `xforms`.`fheight`,
        `xforms`.`fmax`,
        `xforms`.`nroform`,
        `xforms`.`Simport`,
        `xforms`.`Sclose` AS `sclose`,
        `xforms`.`Sexport` AS `sexport`
      FROM
        (`xforms` 
          JOIN `xgrid`)
      WHERE
        (`xforms`.`Idform` = `xgrid`.`xform`);

#
# View "xqreportespec"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `xqreportespec`
    AS
      SELECT
        `xreportespec`.`Id`,
        `xreportespec`.`reporte`,
        `xreportespec`.`nombre`,
        `xreportespec`.`usuario`,
        `xreportespec`.`global`,
        `xreportespec`.`fecha`,
        `xuser`.`name`
      FROM
        (`xreportespec` 
          JOIN `xuser`)
      WHERE
        (`xuser`.`Id` = `xreportespec`.`usuario`);

#
# View "xqreportfilter"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `xqreportfilter`
    AS
      SELECT
        `xreportfilter`.`Id`,
        `xreportfilter`.`Idreport`,
        `xreportfilter`.`cfield`,
        `xreportfilter`.`ctitle`,
        `xreportfilter`.`ctype`,
        `xreportfilter`.`CValues`,
        `xreportfilter`.`xquery`,
        `xreports`.`Id` AS `IDRR`
      FROM
        (`xreportfilter` 
          LEFT JOIN `xreports` ON ((`xreportfilter`.`Idreport` = `xreports`.`tipo`)));

#
# View "xqselect"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `xqselect`
    AS
      SELECT
        `xuser`.`Id` AS `id`, `xuser`.`name` AS `description`
      FROM
        `xuser`;

#
# View "xqueryfilter"
#

CREATE
  ALGORITHM=UNDEFINED
  DEFINER=`root`@`localhost`
  SQL SECURITY DEFINER
  VIEW `xqueryfilter`
    AS
      SELECT
        `xforms`.`cform` AS `code`, `xforms`.`descripcion` AS `name`
      FROM
        `xforms`;
