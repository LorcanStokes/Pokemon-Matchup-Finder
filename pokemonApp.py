"""
Effective Pokémon finder - app
Created by Lorcan Stokes-Rodriguez - 2025

Description:
A Flask web application that suggests the top 10 effective Pokémon 
against a given target, based on type matchups

Usage:
Run the script and it will open a UI in the browser

"""

from flask import Flask, request, jsonify, render_template_string
import pandas as pd

app = Flask(__name__)

# -----------------------------
# Load Excel data once
# -----------------------------
xls = pd.read_excel('pokemonStats.xlsx', sheet_name=['Sheet1', 'Sheet2'])
pokemon_df = xls['Sheet1']
type_chart_df = xls['Sheet2']


# -----------------------------
# Helper function to get effective Pokémon
# -----------------------------
def get_effective_pokemon(pokemon_name):
    if pokemon_name not in pokemon_df['Name'].values:
        return pd.DataFrame()

    idx = pokemon_df.index[pokemon_df['Name'] == pokemon_name][0]
    type1 = pokemon_df.at[idx, 'Type 1']
    type2 = pokemon_df.at[idx, 'Type 2']

    if pd.notna(type2):
        most_eff = type_chart_df.loc[
            (type_chart_df[type1] == 2) & (type_chart_df[type2] == 2),
            'Type'
        ].to_numpy()
        super_eff = type_chart_df.loc[
            ((type_chart_df[type1] == 2) & (type_chart_df[type2] == 1)) |
            ((type_chart_df[type1] == 1) & (type_chart_df[type2] == 2)),
            'Type'
        ].to_numpy()

        # Fallback to super effective if no most effective
        if most_eff.size == 0 and super_eff.size > 0:
            most_eff = super_eff
            super_eff = None

        if super_eff is not None:
            mask = (
                (pokemon_df['Type 1'].isin(most_eff)) &
                ((pokemon_df['Type 2'].isin(super_eff)) | pokemon_df['Type 2'].isna())
            )
        else:
            mask = (
                (pokemon_df['Type 1'].isin(most_eff)) &
                ((pokemon_df['Type 2'].isin(most_eff)) | pokemon_df['Type 2'].isna())
            )

    else:
        most_eff = type_chart_df.loc[type_chart_df[type1] == 2, 'Type'].to_numpy()
        # Single-type fallback (not usually needed, but just in case)
        if most_eff.size == 0:
            most_eff = type_chart_df.loc[type_chart_df[type1] == 1, 'Type'].to_numpy()

        mask = (
            (pokemon_df['Type 1'].isin(most_eff)) &
            ((pokemon_df['Type 2'].isin(most_eff)) | pokemon_df['Type 2'].isna())
        )

    capable = pokemon_df[mask]
    return capable.nlargest(10, 'Attack')


# -----------------------------
# Route: main page (served by Flask)
# -----------------------------
@app.route('/')
def index():
    # HTML template served directly
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Pokémon Effectiveness Finder</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body>
    <div class="container mt-5">
        <h2>Find Top 10 Effective Pokémon</h2>
        <div class="mb-3">
            <label for="pokemon_name" class="form-label">Enter Pokémon Name:</label>
            <input type="text" id="pokemon_name" class="form-control" placeholder="e.g., Pikachu">
        </div>
        <button id="submit_btn" class="btn btn-primary mb-4">Submit</button>
        <div id="results"></div>
    </div>

    <script>
    document.getElementById('submit_btn').addEventListener('click', async () => {
        const name = document.getElementById('pokemon_name').value.trim();
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';

        if (!name) {
            resultsDiv.innerHTML = '<p>Please enter a Pokémon name.</p>';
            return;
        }

        try {
            const response = await fetch('/api/effective', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pokemon_name: name })
            });

            if (!response.ok) {
                const error = await response.json();
                resultsDiv.innerHTML = `<p>${error.error}</p>`;
                return;
            }

            const data = await response.json();

            let table = `<table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Type 1</th>
                                    <th>Type 2</th>
                                    <th>HP</th>
                                    <th>Attack</th>
                                    <th>Defense</th>
                                    <th>Sp. Attack</th>
                                    <th>Sp. Defense</th>
                                    <th>Speed</th>
                                </tr>
                            </thead><tbody>`;

            data.forEach(p => {
                table += `<tr>
                            <td>${p['Name']}</td>
                            <td>${p['Type 1']}</td>
                            <td>${p['Type 2'] || ''}</td>
                            <td>${p['HP']}</td>
                            <td>${p['Attack']}</td>
                            <td>${p['Defense']}</td>
                            <td>${p['Sp.Attack']}</td>
                            <td>${p['Sp.Defense']}</td>
                            <td>${p['Speed']}</td>  
                          </tr>`;
            });


            table += '</tbody></table>';
            resultsDiv.innerHTML = table;

        } catch (err) {
            resultsDiv.innerHTML = `<p>Error: ${err.message}</p>`;
        }
    });
    </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

# -----------------------------
# Route: API endpoint
# -----------------------------
@app.route('/api/effective', methods=['POST'])
def api_effective():
    data = request.json
    pokemon_name = data.get('pokemon_name', '').strip()
    top_pokemon_df = get_effective_pokemon(pokemon_name)

    if top_pokemon_df.empty:
        return jsonify({"error": "Pokémon not found or no capable Pokémon."}), 404

    # Use the exact column names from your Excel file
    cols = ['Name', 'Type 1', 'Type 2', 'HP', 'Attack', 'Defense', 'Sp.Attack', 'Sp.Defense', 'Speed']
    top_pokemon_df = top_pokemon_df[cols].where(pd.notna(top_pokemon_df), None)

    result = top_pokemon_df.to_dict(orient='records')
    return jsonify(result)


# -----------------------------
# Run Flask app
# -----------------------------
if __name__ == '__main__':
    import threading, webbrowser, os

    # Only open the browser if this is the main process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        def open_browser():
            webbrowser.open_new("http://127.0.0.1:5000/")
        threading.Timer(1, open_browser).start()

    app.run(debug=True)


