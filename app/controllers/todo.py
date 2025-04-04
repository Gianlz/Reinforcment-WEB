from app.models.todo import TodoTable
from app.database import engine
from sqlalchemy.orm import query, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from functools import wraps


SessionLocal = sessionmaker(bind=engine)

@contextmanager
def db_session():
    """Gerenciador de contexto para operações com banco de dados"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        session.close()


def db_handler(func):
    """Decorator para gerenciar sessões de banco de dados automaticamente"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_session() as session:
            try:
                return func(session, *args, **kwargs)
            except SQLAlchemyError as e:
                raise RuntimeError(f"Database error {str(e)}")
    return wrapper


@db_handler
def add_to_DB(session, name: str, description = "") -> None:
    """Adiciona novo TODO para o banco de dados"""
    tabela = TodoTable(name, description)
    session.add(tabela)
    
    
@db_handler
def get_all(session):
    query_result = session.query(TodoTable).all()
    result = []
    for item in query_result:
        todo = {
            "_id": item._id,
            "name": item.name,
            "description": item.description,
            "completed": item.completed,
            "creation_date": item.creation_date
        }
        result.append(todo)
        
    return result

@db_handler
def mark_task_completed(session, task_id):
    """Muda a flag da tarefa para completada = True"""
    query_result = session.query(TodoTable).filter(TodoTable._id == task_id).first()
    if query_result:
        query_result.completed = True
        return True
    return False

@db_handler
def delete_task_by_id(session, task_id):
    """Deleta a task do banco de dados pelo ID"""
    query_result = session.query(TodoTable).filter(TodoTable._id == task_id).first()
    if query_result:
        session.delete(query_result)
        return True
    return False


