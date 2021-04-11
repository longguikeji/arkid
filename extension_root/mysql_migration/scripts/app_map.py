#!/usr/bin/env python3

"""
CREATE TABLE `oneid_meta_app` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `is_del` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `created` datetime(6) DEFAULT NULL,
  `uid` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `remark` longtext NOT NULL,
  `editable` tinyint(1) NOT NULL,
  `allow_any_user` tinyint(1) NOT NULL,
  `logo` longtext,
  `index` varchar(512),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `app_app` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `is_del` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `created` datetime(6) DEFAULT NULL,
  `name` varchar(128) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `description` longtext,
  `tenant_id` int NOT NULL,
  `type` varchar(128) NOT NULL,
  `data` json NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `app_app_tenant_id_98105ca0_fk_tenant_tenant_id` (`tenant_id`),
  CONSTRAINT `app_app_tenant_id_98105ca0_fk_tenant_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenant_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

app_table_map = ('oneid_meta_app', 'app_app')
app_column_map = {
    # "id": "id",
    'uuid': 'uuid',
    'is_del': 'is_del',
    'is_active': 'is_active',
    'updated': 'updated',
    'created': 'created',
    'uid': '',
    'name': 'name',
    'remark': 'description',
    'editable': '',
    'allow_any_user': '',
    'logo': 'logo',
    'index': '',
}
