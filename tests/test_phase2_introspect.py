import os
import sys

# Add the project root to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from app.db.introspect import build_catalog

Base = declarative_base()

class ValidTable(Base):
    __tablename__ = 'valid_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Removed NoPkTable class definition to avoid ORM error
# We will create this table using raw SQL below.

class SecretTable(Base):
    __tablename__ = 'secret_table'
    id = Column(Integer, primary_key=True)
    secret_code = Column(String)

class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('valid_table.id'))

def test_phase2_introspect():
    # Use an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create a table without a PK using raw SQL because ORM forces PK
    with engine.connect() as conn:
        conn.exec_driver_sql("CREATE TABLE no_pk_table (name TEXT)")
        conn.commit()

    catalog = build_catalog(engine)
    exposed = catalog['exposed_tables']
    tables = catalog['tables']

    print("Exposed tables:", exposed)

    # 1. Valid Table should be present
    assert 'valid_table' in exposed, "valid_table should be exposed"

    # 2. No PK Table should be filtered
    assert 'no_pk_table' not in exposed, "no_pk_table should be filtered (no PK)"

    # 3. Secret Table should be filtered based on name
    assert 'secret_table' not in exposed, "secret_table should be filtered (sensitive name)"

    # 4. Orders should be present and have FK
    assert 'orders' in exposed, "orders should be exposed"
    orders_meta = tables['orders']
    fks = orders_meta.get('foreign_keys', [])
    assert len(fks) > 0, "orders should have foreign keys detected"
    assert fks[0]['referred_table'] == 'valid_table', "orders should refer to valid_table"

    print("✅ Phase 2 Introspection Verification Passed!")

if __name__ == "__main__":
    test_phase2_introspect()
