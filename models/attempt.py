from database import db #check for this file in the folder you are existing
from datetime import datetime
class QuizAttempt(db.Model):  
    """Tracks each attempt of a user on a quiz."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    time_started = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    time_completed = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="in_progress", nullable=False)  # in_progress, completed, abandoned

    # Relationship to answers
    answers = db.relationship('UserAnswer', backref='attempt', lazy=True, cascade="all, delete")
    scores = db.relationship('Scores', backref='attempt', lazy=True, cascade="all, delete")

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False)
    total_scored = db.Column(db.Float)


class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('option.id'),nullable=True)
    score = db.Column(db.Float, default=0.0)
    question = db.relationship("Question", backref="user_answers")
    selected_option = db.relationship("Option", backref="user_answers", foreign_keys=[selected_option_id])
    