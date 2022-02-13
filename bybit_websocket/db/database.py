import sqlalchemy

engine = sqlalchemy.create_engine("sqlite:///:memory:")

SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = sqlalchemy.orm.declarative_base()