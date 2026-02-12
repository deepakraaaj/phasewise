import os
import sys

# Add the project root to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base
from app.db.introspect import build_catalog
import datetime

Base = declarative_base()

class UserTable(Base):
    __tablename__ = 'users_test' # using users_test specifically to avoid guard block on 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False) # Should be in create_fields
    email = Column(String, nullable=True)     # Nullable -> not in create_fields
    status = Column(String, server_default="active", nullable=False) # Has default -> not in create_fields
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP")) # System col -> not in create_fields, not in update_fields

def test_phase3_forms():
    # Use an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    
    # Create tables
    Base.metadata.create_all(engine)

    catalog = build_catalog(engine)
    exposed = catalog['exposed_tables']
    tables = catalog['tables']

    print("Exposed tables:", exposed)
    assert 'users_test' in exposed, "users_test should be exposed"

    t_meta = tables['users_test']
    
    # 1. Verify create_fields
    # Expect: ['username'] only.
    # 'id' is PK (auto). 'email' is nullable. 'status' has default. 'created_at' has default.
    print("Create fields:", t_meta['create_fields'])
    assert 'username' in t_meta['create_fields'], "username SHOULD be a required create field (not null, no default)"
    assert 'email' not in t_meta['create_fields'], "email is nullable, should NOT be required"
    assert 'status' not in t_meta['create_fields'], "status has default, should NOT be required"
    assert 'id' not in t_meta['create_fields'], "id is PK, should NOT be required"

    # 2. Verify update_fields
    # Expect: username, email, status.
    # Exclude: id (PK), created_at (audit)
    print("Update fields:", t_meta['update_fields'])
    assert 'username' in t_meta['update_fields']
    assert 'email' in t_meta['update_fields']
    assert 'status' in t_meta['update_fields']
    assert 'id' not in t_meta['update_fields'], "PK should not be updateable"
    assert 'created_at' not in t_meta['update_fields'], "Audit col should not be updateable"

    # 3. Verify filter_fields
    # Expect: id (PK) and created_at (common key) and email (common key) and status (common key)
    print("Filter fields:", t_meta['filter_fields'])
    assert 'id' in t_meta['filter_fields']
    assert 'created_at' in t_meta['filter_fields']
    assert 'email' in t_meta['filter_fields']
    assert 'status' in t_meta['filter_fields']

    print("✅ Phase 3 Conversational Forms Verification Passed!")

if __name__ == "__main__":
    test_phase3_forms()
