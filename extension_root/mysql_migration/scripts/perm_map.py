#!/usr/bin/env python3

"""
CREATE TABLE `oneid_meta_perm` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `is_del` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `created` datetime(6) DEFAULT NULL,
  `uid` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `remark` longtext NOT NULL,
  `scope` varchar(128) NOT NULL,
  `action` varchar(128) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `default_value` tinyint(1) NOT NULL,
  `editable` tinyint(1) NOT NULL,
  `sub_account_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `oneid_meta_perm_uid_744ff75e_uniq` (`uid`),
  KEY `oneid_meta_perm_sub_account_id_f29cb92f_fk_oneid_met` (`sub_account_id`),
  CONSTRAINT `oneid_meta_perm_sub_account_id_f29cb92f_fk_oneid_met` FOREIGN KEY (`sub_account_id`) REFERENCES `oneid_meta_subaccount` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `inventory_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `is_del` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `created` datetime(6) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `codename` varchar(100) NOT NULL,
  `content_type_id` int NOT NULL,
  `tenant_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `inventory_permission_content_type_id_codename_fd306f53_uniq` (`content_type_id`,`codename`),
  KEY `inventory_permission_tenant_id_39673570_fk_tenant_tenant_id` (`tenant_id`),
  CONSTRAINT `inventory_permission_content_type_id_92780a64_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `inventory_permission_tenant_id_39673570_fk_tenant_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenant_tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

perm_table_map = ('oneid_meta_perm', 'inventory_permission')
perm_column_map = {
    # "id": "id",
    'uuid': 'uuid',
    'is_del': 'is_del',
    'is_active': 'is_active',
    'updated': 'updated',
    'created': 'created',
    'uid': 'codename',
    'name': 'name',
    'remark': '',
    'scope': '',
    'action': '',
    'subject': '',
    'default_value': '',
    'editable': '',
    'sub_account_id': '',
}
