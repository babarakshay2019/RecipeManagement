import json
import logging
from json import JSONDecodeError

from flask import Flask, jsonify, request
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import Recipe, User, session
from schema import RecipeSchema, UserSchema

user_schema = UserSchema()
recipe_schema = RecipeSchema()


def register_routes(app, RECIPES_PER_PAGE, session):
    @app.route('/api/register', methods=['POST'])
    def register_user():
        data = request.get_json()

        required_fields = {'username', 'email', 'password'}
        if not required_fields.issubset(data.keys()):
            return jsonify({'error': 'Missing field(s)'}), 400

        username = data['username'].lower()
        email = data['email'].lower()
        password = data['password']

        if len(password) < 8:
          return jsonify({'error': 'Weak password'}), 400

        existing_user = session.query(User).filter(
            (User.username.ilike(username)) | (User.email.ilike(email))
        ).first()

        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        session.add(new_user)
        session.commit()
        return jsonify({'message': 'User registered successfully'}), 201


    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({'error': 'Missing username or password'}), 400

            user = session.query(User).filter_by(username=username).first()

            if user is None or not check_password_hash(user.password, password):
                return jsonify({'error': 'Invalid username or password'}), 401

            login_user(user)
            return jsonify({'message': 'Login successful'})

        except Exception as e:
            return jsonify({'error': 'An error occurred during login: {}'.format(str(e))}), 500

    # CRUD Endpoints for Recipes

    @app.route('/api/recipes', methods=['GET'])
    def get_recipes():
        """
        A function to retrieve a list of recipes based on the requested page number.
        Uses the page parameter to calculate the offset for querying recipes from the database.
        """
        try:
            page = request.args.get('page', 1, type=int)
            offset = (page - 1) * RECIPES_PER_PAGE
            recipes = Recipe.query.offset(offset).limit(RECIPES_PER_PAGE).all()

            if not recipes:
                return jsonify({'message': 'No recipes found'}), 404

            modified_recipes = []
            for recipe in recipes:
                try:
                    # Deserialize ingredients string to list
                    ingredients = json.loads(recipe.ingredients)
                    if not isinstance(ingredients, list):
                        raise ValueError('Ingredients must be a list')
                    # Ensure all ingredients have a 'quantity' key, if not, add it with an empty string
                    for ingredient in ingredients:
                        if 'quantity' not in ingredient:
                            ingredient['quantity'] = ''
                except (json.JSONDecodeError, ValueError) as e:
                    # Skip processing the recipe if ingredients are empty or invalid
                    app.logger.error(
                        f'Error processing recipe with ID {recipe.id}: {str(e)}')
                    continue

                # Update recipe object with modified ingredients list
                modified_recipe = recipe.serialize()
                modified_recipe['ingredients'] = ingredients
                modified_recipes.append(modified_recipe)

            return jsonify(modified_recipes)
        except Exception as e:
            return jsonify({'error': 'An error occurred during recipe retrieval: {}'.format(str(e))}), 500

    @app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
    def get_recipe(recipe_id):
        try:
            recipe = session.query(Recipe).get(recipe_id)
            if recipe is None:
                return jsonify({'error': 'Recipe not found'}), 404

            # Deserialize ingredients string to list
            ingredients = json.loads(recipe.ingredients)

            # Ensure all ingredients have a 'quantity' key, if not, add it with an empty string
            for ingredient in ingredients:
                if 'quantity' not in ingredient:
                    ingredient['quantity'] = ''

            # Update recipe object with modified ingredients list
            recipe.ingredients = json.dumps(ingredients)

            return jsonify(recipe.serialize())

        except Exception as e:
            return jsonify({'error': 'An error occurred during recipe retrieval: {}'.format(str(e))}), 500

    @app.route('/api/recipes', methods=['POST'])
    def create_recipe():
        if not current_user.is_authenticated:
            return jsonify({'error': 'User not authenticated'}), 401

        try:
            data = request.get_json()

            # Define required fields and disallowed fields
            required_fields = {'title', 'description',
                               'instructions', 'ingredients'}
            disallowed_fields = {'created_by', 'id'}

            # Check for disallowed fields
            for field in disallowed_fields:
                if field in data:
                    return jsonify({'error': f'Field "{field}" is not allowed'}), 400

            # Check if all required fields are provided
            missing_fields = required_fields - set(data.keys())
            if missing_fields:
                return jsonify({'error': f'Missing field(s): {", ".join(missing_fields)}'}), 400

            # Ensure ingredients is a list of dictionaries
            ingredients = data.get('ingredients')
            if not isinstance(ingredients, list):
                return jsonify({'error': 'Ingredients must be a list of dictionaries'}), 400

            # Check if each ingredient is a dictionary with 'name' and 'quantity' keys
            for ingredient in ingredients:
                if not isinstance(ingredient, dict) or 'name' not in ingredient:
                    return jsonify({'error': 'Each ingredient must be a dictionary with "name" key'}), 400

            # Convert ingredients to JSON string
            ingredients_json = json.dumps(ingredients)

            new_recipe = Recipe(
                title=data['title'],
                description=data['description'],
                instructions=data['instructions'],
                created_by=current_user.id,
                ingredients=ingredients_json  # Pass the JSON string
            )

            session.add(new_recipe)
            session.commit()
            return jsonify(new_recipe.serialize()), 201

        except Exception as e:
            return jsonify({'error': f'An error occurred during recipe creation: {str(e)}'}), 500

    @app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
    def update_recipe(recipe_id):
        try:
            recipe = session.query(Recipe).filter_by(id=recipe_id).first()

            # Check if the recipe exists
            if not recipe:
                return jsonify({'error': 'Recipe not found'}), 404

            # Check if the current user is the creator of the recipe
            if recipe.created_by != current_user.id:
                return jsonify({'error': 'You are not the creator of this recipe'}), 403

            data = request.get_json()

            # Update the recipe fields
            recipe.title = data.get('title', recipe.title)
            recipe.description = data.get('description', recipe.description)

            # Update ingredients only if provided in the request
            if 'ingredients' in data:
                new_ingredients = data['ingredients']
                if not isinstance(new_ingredients, list):
                    return jsonify({'error': 'Ingredients must be a list of dictionaries'}), 400
                recipe.ingredients = json.dumps(new_ingredients)

            recipe.instructions = data.get('instructions', recipe.instructions)

            session.commit()
            return jsonify(recipe.serialize())

        except Exception as e:
            return jsonify({'error': f'An error occurred during recipe update: {str(e)}'}), 500

    @app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
    def delete_recipe(recipe_id):
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()

        # Check if the recipe exists
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        # Check if the current user is the creator of the recipe
        if recipe.created_by != current_user.id:
            return jsonify({'error': 'You are not authorized to delete this recipe'}), 403

        session.delete(recipe)
        session.commit()
        return jsonify({'message': 'Recipe deleted successfully'})

    # Endpoint for adding ingredients to a recipe
    @app.route('/api/recipes/<int:recipe_id>/ingredients', methods=['POST'])
    def add_ingredients(recipe_id):
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()

        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        if recipe.created_by != current_user.id:
            return jsonify({'error': 'You are not authorized to modify this recipe'}), 403

        data = request.get_json()

        if not data:
            return jsonify({'error': 'Invalid JSON format or empty request body'}), 400

        new_ingredients = data.get('ingredients', [])

        if not isinstance(new_ingredients, list):
            return jsonify({'error': 'Ingredients must be a list'}), 400

        # Deserialize the existing ingredients from JSON string to a Python list
        existing_ingredients = json.loads(recipe.ingredients)

        # Append the new ingredients to the existing list
        existing_ingredients.extend(new_ingredients)

        # Serialize the updated list back into a JSON string
        updated_ingredients_json = json.dumps(existing_ingredients)

        # Update the recipe's ingredients field with the updated JSON string
        recipe.ingredients = updated_ingredients_json

        session.commit()

        return jsonify(recipe.serialize())

    # Search functionality for recipes by title or ingredients
    @app.route('/api/recipes/search', methods=['GET'])
    def search_recipes():
        keyword = request.args.get('q')
        if not keyword:
            return jsonify({'error': 'Query parameter "q" is required for search'}), 400

        try:
            # Check if the user is authenticated
            if not current_user.is_authenticated:
                return jsonify({'error': 'User not authenticated'}), 401

            # Search by title or ingredients only for recipes created by the authenticated user
            recipes = session.query(Recipe).filter(
                (Recipe.created_by == current_user.id) &
                ((Recipe.title.ilike(f'%{keyword}%')) | (
                    Recipe.ingredients.ilike(f'%{keyword}%')))
            ).all()

            return jsonify([recipe.serialize() for recipe in recipes])

        except Exception as e:
            return jsonify({'error': 'An error occurred during search: ' + str(e)}), 500
