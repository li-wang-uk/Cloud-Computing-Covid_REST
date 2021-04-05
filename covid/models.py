from covid import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id): # method for login_manager to know the user_id of the current_user
    return User.query.get(int(user_id))


# model for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # User ID: primary key
    username = db.Column(db.String(30), unique=True, nullable=False) # username: UNIQUE, NOT NULL
    password = db.Column(db.String(60), nullable=False) # password: NOT NULL, stored as a hashed password, not plaintext that the user inputs
    favorite_countries = db.relationship("Favorite", backref="favorite_user", lazy=True) # User has one-to-many relationship with Favorite: one(User) to many(Favorite)

    def __repr__(self):
        return f"User('{self.username}')"


# model for favorite countries
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Favorite ID: primary key
    slug = db.Column(db.String(20), nullable=False) # slug code for countries (e.g., united-kingdom, japan), NOT NULL
    watchlevel = db.Column(db.String(20), nullable=False) # watchlevel of the country (priority for the user)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) # user_id of the user who has relation with the Favorite

    def __repr__(self):
        return f"Post('{self.slug}', '{self.watchlevel}', '{self.user_id}')"
