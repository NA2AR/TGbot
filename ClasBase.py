import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship 

Base = declarative_base()

class Student(Base):
    __tablename__ = "Student"
    
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'{self.id}:{self.name}'
    
class Words(Base):
    __tablename__ = "Words"
    
    id = sq.Column(sq.Integer, primary_key=True)
    words = sq.Column(sq.String(length=20), unique=True)
    translate = sq.Column(sq.String(length=20), unique=True)
    
    def __str__(self):
        return f'{self.id}:{self.words}:{self.translate}'
    
class StudentWords(Base):
    __tablename__ = "StudentWords"

    id = sq.Column(sq.Integer, primary_key=True)
    words_id = sq.Column(sq.Integer, sq.ForeignKey("Words.id"), nullable=False)
    Student_id = sq.Column(sq.Integer, sq.ForeignKey("Student.id"), nullable=False)
    
    words = relationship(Words, backref="StudentWords")
    student = relationship(Student, backref="StudentWords")
    
    def __str__(self):
        return f'{self.id}:({self.words_id}-{self.Student_id})'

def create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)