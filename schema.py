from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models import Recipe, User


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class RecipeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Recipe
        load_instance = True
