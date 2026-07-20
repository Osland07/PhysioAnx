import os
import sys

# Add app to path so we can import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from models.database import SessionLocal, engine
from models.patient import Patient

def migrate_ids():
    session = SessionLocal()
    try:
        patients = session.query(Patient).order_by(Patient.id.asc()).all()
        for idx, patient in enumerate(patients, start=1):
            new_id = f"ID{idx:05d}"
            print(f"Updating patient ID {patient.id}: {patient.no_rm} -> {new_id}")
            patient.no_rm = new_id
        session.commit()
        print("Database migration complete.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    migrate_ids()
