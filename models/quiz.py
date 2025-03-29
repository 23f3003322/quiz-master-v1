
from database import db


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250))
    chapters = db.relationship('Chapter', backref='subject', lazy=True,cascade="all, delete")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True,cascade="all, delete")

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    remarks = db.Column(db.Text)
    date_of_quiz = db.Column(db.Date, nullable=False)
    
    # New fields
    start_time = db.Column(db.Time, nullable=False)  # Quiz start time (HH:MM)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes

    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete")
    attempts = db.relationship('Scores', backref='quiz', lazy=True, cascade="all, delete")



class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(10))  # 'msq' or 'mcq'
    score = db.Column(db.Float, default=1.0, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    options = db.relationship('Option', backref='question', lazy=True,cascade="all, delete")

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_text = db.Column(db.String(250), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

