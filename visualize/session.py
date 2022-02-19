import sqlalchemy

# engine = sqlalchemy.create_engine("sqlite:///:memory:")
engine = sqlalchemy.create_engine("sqlite:///example.db")

SessionLocal = sqlalchemy.orm.sessionmaker(bind=engine, autocommit=False, autoflush=False)