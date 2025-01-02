from flask import Flask, render_template, request, jsonify
from poultry_formulation import get_formulation, nutrient_requirements, ingredient_db

app = Flask(__name__)

@app.route('/')
def home():
    # Pass data for poultry classes and ingredient categories to the template
    poultry_classes = nutrient_requirements.keys()
    ingredient_options = {
        "energy_sources": [name for name, details in ingredient_db.items() if details['type'] == 'energy' and details['subtype'] == 'source'],
        "energy_replacers": [name for name, details in ingredient_db.items() if details['type'] == 'energy' and details['subtype'] == 'replacer'],
        "high_protein_sources": [name for name, details in ingredient_db.items() if details['type'] == 'protein' and details['subtype'] == 'high'],
        "medium_protein_sources": [name for name, details in ingredient_db.items() if details['type'] == 'protein' and details['subtype'] == 'medium'],
        "protein_replacers": [name for name, details in ingredient_db.items() if details['type'] == 'protein' and details['subtype'] == 'replacer'],
        "amino_acid_1": [name for name, details in ingredient_db.items() if details['type'] == 'Amino acid 1'],
        "amino_acid_2": [name for name, details in ingredient_db.items() if details['type'] == 'Amino acid 2']
    }

    return render_template('index.html', poultry_classes=poultry_classes, ingredient_options=ingredient_options)

@app.route('/formulate', methods=['POST'])
def formulate():
    # Handle AJAX request and return JSON response
    data = request.get_json()

    poultry_class = data.get('poultry_class')
    energy_sources = data.get('energy_sources', [])
    energy_replacers = data.get('energy_replacers', [])
    high_protein_sources = data.get('high_protein_sources', [])
    medium_protein_sources = data.get('medium_protein_sources', [])
    protein_replacers = data.get('protein_replacers', [])
    amino_acid_1 = data.get('amino_acid_1', [])
    amino_acid_2 = data.get('amino_acid_2', [])

    # Validate inputs
    if len(energy_sources) < 2 or len(medium_protein_sources) < 2 or len(protein_replacers) < 2 or len(energy_replacers) < 2:
        return jsonify({'error': 'Please select at least 2 items for energy sources, medium protein sources, energy replacers, and protein replacers.'})

    # Generate formulations using the selected inputs
    formulations = get_formulation(
        poultry_class,
        energy_sources,
        energy_replacers,
        high_protein_sources,
        medium_protein_sources,
        protein_replacers,
        amino_acid_1,
        amino_acid_2
    )

    # Add a tolerance margin to include near-matching formulations
    tolerance = 0.01  # 5% tolerance for nutrient requirements
    recommended_formulations = [
        formulation for formulation in formulations
        if (2900 * (1 - tolerance)) <= formulation['total_me_content'] <= (3000 * (1 + tolerance)) and
           (18.0 * (1 - tolerance)) <= formulation['total_cp_content'] <= (20.0 * (1 + tolerance))
    ]

    # Return formulations in JSON format
    return jsonify({'formulations': formulations, 'recommended_formulations': recommended_formulations})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
