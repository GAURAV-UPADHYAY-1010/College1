from flask import Flask, request, render_template, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    recipes = []
    if os.path.exists('recipes.txt'):
        with open('recipes.txt', 'r') as file:
            lines = file.readlines()
            recipe = {}
            for line in lines:
                if line.strip() == "":
                    recipes.append(recipe)
                    recipe = {}
                else:
                    key, value = line.split(": ", 1)
                    recipe[key.strip()] = value.strip()
            if recipe:
                recipes.append(recipe)
    return render_template('index.html', recipes=recipes)

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        file = request.files['image']

        if not name or not ingredients or not instructions or not file:
            flash('All fields are required!')
            return redirect(url_for('add_recipe'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Invalid file type!')
            return redirect(url_for('add_recipe'))

        with open('recipes.txt', 'a') as file:
            file.write(f"Name: {name}\nIngredients: {', '.join(ingredients.split(','))}\nInstructions: {instructions}\nImage: {filename}\n\n")
        
        flash('Recipe added successfully!')
        return redirect(url_for('index'))

    return render_template('add_recipe.html')

@app.route('/view/<name>')
def view_recipe(name):
    if os.path.exists('recipes.txt'):
        with open('recipes.txt', 'r') as file:
            lines = file.readlines()
            recipe = {}
            found = False
            for line in lines:
                if line.startswith("Name: "):
                    if found:
                        break
                    if line.split(": ", 1)[1].strip() == name:
                        found = True
                if found:
                    if line.strip() == "":
                        break
                    key, value = line.split(": ", 1)
                    recipe[key.strip()] = value.strip()
            if found:
                return render_template('view_recipe.html', recipe=recipe)
    flash('Recipe not found.')
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search_recipe():
    keyword = request.form['keyword']
    results = []

    if os.path.exists('recipes.txt'):
        with open('recipes.txt', 'r') as file:
            lines = file.readlines()
            recipe = {}
            for line in lines:
                if line.strip() == "":
                    if any(keyword.lower() in v.lower() for v in recipe.values()):
                        results.append(recipe)
                    recipe = {}
                else:
                    key, value = line.split(": ", 1)
                    recipe[key.strip()] = value.strip()
            if recipe and any(keyword.lower() in v.lower() for v in recipe.values()):
                results.append(recipe)

        if results:
            return render_template('search_results.html', results=results)
        else:
            flash('No matching recipes found.')
            return redirect(url_for('index'))
    else:
        flash('No recipes found.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
