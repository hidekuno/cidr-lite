use cidr;

DROP TABLE IF EXISTS `asn_v4`;
CREATE TABLE `asn_v4` (
  `addr` char(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `prefixlen` smallint DEFAULT NULL,
  `cidr` varchar(18) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `asn` int DEFAULT NULL,
  `provider` text COLLATE utf8mb4_general_ci,
  KEY `asn_v4_idx1` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `asn_v6`;
CREATE TABLE `asn_v6` (
  `addr` char(128) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `prefixlen` smallint DEFAULT NULL,
  `cidr` varchar(43) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `asn` int DEFAULT NULL,
  `provider` text COLLATE utf8mb4_general_ci,
  KEY `asn_v6_idx1` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `city_v4`;
CREATE TABLE `city_v4` (
  `addr` char(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `prefixlen` smallint DEFAULT NULL,
  `cidr` varchar(18) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `city` text COLLATE utf8mb4_general_ci,
  KEY `city_v4_idx1` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `city_v6`;
CREATE TABLE `city_v6` (
  `addr` char(128) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `prefixlen` smallint DEFAULT NULL,
  `cidr` varchar(43) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `city` text COLLATE utf8mb4_general_ci,
  KEY `city_v6_idx1` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `ipaddr_v4`;
CREATE TABLE `ipaddr_v4` (
  `addr` char(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `prefixlen` smallint DEFAULT NULL,
  `cidr` varchar(18) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `country` char(2) COLLATE utf8mb4_general_ci DEFAULT NULL,
  KEY `ipaddr_v4_idx1` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `ipaddr_v6`;
CREATE TABLE `ipaddr_v6` (
  `addr` char(128) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `prefixlen` smallint DEFAULT NULL,
  `cidr` varchar(43) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `country` char(2) COLLATE utf8mb4_general_ci DEFAULT NULL,
  KEY `ipaddr_v6_idx1` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
