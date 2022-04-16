import os
from flask import Flask
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
from app import db,registered_user

class User(db.Model):
    '''User class containing username,password,bookmarks and all ratings of user'''
    __tablename__ = 'user-table'
    global registered_user
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    repass = db.Column(db.String(200))
    ratelist = db.Column(db.String(200))
    bookmarks = db.relationship(
        'Bookmark',
        backref=db.backref('bookmark-table', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, username, password, repass, ratelist):
        self.username = username
        self.password = password
        self.repass = repass
        self.ratelist = ratelist
        self.active = True

    def user_logout(self):
        self.active = False

        
class Contents(db.Model):
    '''Contents class containing all about the news and its rating and comments'''
    __tablename__ = 'contents-table'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    newscontent = db.Column(db.Text)
    subsection = db.Column(db.String(100))
    Title = db.Column(db.String(100))
    rating = db.Column(db.Float)
    image = db.Column(db.String(100))
    images = db.Column(db.String(10000))
    comments = db.relationship(
        'Comment',
        backref=db.backref('contents-table', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    ratings = db.relationship(
        'Rating',
        backref=db.backref('rating-table', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, newscontent, subsection, Title, rating, image, images):
        self.newscontent = newscontent
        self.subsection = subsection
        self.Title = Title
        self.rating = rating
        self.image = image
        self.images = images

class Rating(db.Model):
    '''Rating class containing the rating linked to a specific news id'''
    __tablename__ = 'rating-table'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    contents_id = db.Column(db.Integer, db.ForeignKey(
        'contents-table.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Float)

    def __init__(self, rating, contents_id):
        self.rating = rating
        self.contents_id = contents_id

class Bookmark(db.Model):
    '''Bookmark class containing bookmarked news of the user for a specific news id'''
    __tablename__ = 'bookmark-table'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user-table.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, title, user_id):
        self.title = title
        self.user_id = user_id

class Comment(db.Model):
    '''Comment class containing all the comments given by several users for a specific news id'''
    __tablename__ = 'comment-table'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    contents_id = db.Column(db.Integer, db.ForeignKey(
        'contents-table.id', ondelete='CASCADE'), nullable=False)
    comm = db.Column(db.String(500))
    username = db.Column(db.String(200))

    def __init__(self, comm, username, contents_id):
        self.comm = comm
        self.username = username
        self.contents_id = contents_id
