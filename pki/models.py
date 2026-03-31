import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class IssuedCertificate(Base):
    __tablename__ = "issued_certificates"
    id           = Column(Integer, primary_key=True)
    serial       = Column(String, unique=True, index=True)
    common_name  = Column(String, nullable=False)
    cert_type    = Column(String, default="tls_server")
    cert_pem     = Column(Text, nullable=False)
    issued_at    = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at   = Column(DateTime, nullable=False)
    is_revoked   = Column(Boolean, default=False)
    revoked_at   = Column(DateTime, nullable=True)
    revoke_reason = Column(String, nullable=True)

class APIUser(Base):
    __tablename__ = "api_users"
    id            = Column(Integer, primary_key=True)
    username      = Column(String, unique=True)
    hashed_password = Column(String)
    role          = Column(String, default="operator")  # admin | operator | auditor
    created_at    = Column(DateTime, default=datetime.datetime.utcnow)
