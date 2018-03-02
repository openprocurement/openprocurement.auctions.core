# -*- coding: utf-8 -*-
# MigrateTest


def migrate(self):
    self.assertEqual(self.get_db_schema_version(self.db), self.schema_version)
    self.migrate_data(self.app.app.registry, 1)
    self.assertEqual(self.get_db_schema_version(self.db), self.schema_version)
