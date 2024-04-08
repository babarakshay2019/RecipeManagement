# Recipe Management System

This project is a Recipe Management System built with Flask.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your_username/RecipeManagement.git
    ```

2. Navigate to the project directory:

    ```bash
    cd RecipeManagement
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv env
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        env\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source env/bin/activate
        ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Run the application:

    ```bash
    python main.py
    ```

7. Run Test Cases:

    ```bash
    python -m unittest
    ```
## Usage

- Once the application is running, navigate to [http://localhost:5000](http://localhost:5000) in your web browser.

- You can register a new user via [http://localhost:5000/api/register](http://localhost:5000/api/register) link and filling out the registration form.

- After registering, you can log in with your username and password. [http://localhost:5000/api/login](http://localhost:5000/api/login)

- Once logged in, you can manage your recipes by adding, editing, or deleting them.

- You can add your receipe from POST method [http://localhost:5000/api/recipes](http://localhost:5000/api/recipes)

- Your all recipes GET method [http://localhost:5000/api/recipes](http://localhost:5000/api/recipes)

- Specific Recipe GET method [http://localhost:5000/api/recipes/recipe_id](http://localhost:5000/api/recipes/1)

- Update Recipe PUT method [http://localhost:5000/api/recipes/recipe_id](http://localhost:5000/api/recipes/1)

- Delete Recipe DELETE method [http://localhost:5000/api/recipes/recipe_id](http://localhost:5000/api/recipes/1)

- Add ingredients for existing Recipe POST method [http://localhost:5000/api/recipes/recipe_id/ingredients](http://localhost:5000/api/recipes/1/ingredients)

- Search Recipe from title or ingredients GET method  [http://localhost:5000/api/recipes/](http://localhost:5000/api/recipes/search?q=dabeli)

