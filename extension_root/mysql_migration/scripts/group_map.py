#!/usr/bin/env python3

"""
CREATE TABLE `oneid_meta_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `is_del` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `created` datetime(6) DEFAULT NULL,
  `uid` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `remark` longtext NOT NULL,
  `parent_id` int DEFAULT NULL,
  `accept_user` tinyint(1) NOT NULL,
  `order_no` int NOT NULL,
  `top` varchar(255) NOT NULL,
  `node_scope` longtext NOT NULL,
  `user_scope` longtext NOT NULL,
  `visibility` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `oneid_meta_group_parent_id_9a86291d_fk_oneid_meta_group_id` (`parent_id`),
  KEY `group_uid_index` (`uid`),
  CONSTRAINT `oneid_meta_group_parent_id_9a86291d_fk_oneid_meta_group_id` FOREIGN KEY (`parent_id`) REFERENCES `oneid_meta_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `inventory_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` char(32) NOT NULL,
  `is_del` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `created` datetime(6) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `tenant_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `inventory_group_tenant_id_490349aa_fk_tenant_tenant_id` (`tenant_id`),
  KEY `inventory_group_parent_id_a62fe204_fk_inventory_group_id` (`parent_id`),
  CONSTRAINT `inventory_group_parent_id_a62fe204_fk_inventory_group_id` FOREIGN KEY (`parent_id`) REFERENCES `inventory_group` (`id`),
  CONSTRAINT `inventory_group_tenant_id_490349aa_fk_tenant_tenant_id` FOREIGN KEY (`tenant_id`) REFERENCES `tenant_tenant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
"""

group_table_map = ('oneid_meta_group', 'inventory_group')
group_column_map = {
    # 'id': 'id',
    'uuid': 'uuid',
    'is_del': 'is_del',
    'is_active': 'is_active',
    'updated': 'updated',
    'created': 'created',
    'uid': '',
    'name': 'name',
    'remark': '',
    # 'parent_id': 'parent_id',
    'accept_user': '',
    'order_no': '',
    'top': '',
    'node_scope': '',
    'user_scope': '',
    'visibility': '',
}
