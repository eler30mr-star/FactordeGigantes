"""Prueba local de migración D1 sin tocar la base real de Cloudflare."""
import sqlite3
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class EditorialMigrationTests(unittest.TestCase):
    def test_additive_migration_integrity(self):
        db=sqlite3.connect(":memory:")
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.executescript((ROOT/"migrations/0001_initial.sql").read_text())
            db.executescript((ROOT/"migrations/0002_editorial_dossiers.sql").read_text())
            # Migración CREATE IF NOT EXISTS idempotente cuando se corre como SQL directamente.
            db.executescript((ROOT/"migrations/0002_editorial_dossiers.sql").read_text())
            db.execute(
                "INSERT INTO jobs(id,title,format,status,manifest_json) VALUES (?,?,?,?,?)",
                ("abc","Expediente de prueba","short","draft","{}"),
            )
            db.execute("INSERT INTO editorial_dossiers(job_id,dossier_json) VALUES (?,?)",("abc","{}"))
            db.execute(
                "UPDATE editorial_dossiers SET editor_attested=1, editor_name=?, attested_at=datetime('now') WHERE job_id=?",
                ("Editor de prueba","abc"),
            )
            got=db.execute("SELECT editor_attested, editor_name FROM editorial_dossiers WHERE job_id='abc'").fetchone()
            self.assertEqual(got,(1,"Editor de prueba"))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO editorial_dossiers(job_id,dossier_json) VALUES (?,?)",("missing","{}"))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE editorial_dossiers SET editor_attested=3 WHERE job_id='abc'")
            self.assertTrue(db.execute("SELECT name FROM sqlite_master WHERE name='events'").fetchone())
        finally:
            db.close()


if __name__=="__main__":
    unittest.main()
