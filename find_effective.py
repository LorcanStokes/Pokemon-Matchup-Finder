"""
Effective Pokémon finder
Created by Lorcan Stokes-Rodriguez - 2025

Description:
A Flask web application that suggests the top 10 effective Pokémon 
against a given target, based on type matchups

Usage:
Change the target Pokémon in the main and run or run >> python -c "from find_effective import findMostEffective; print(findMostEffective('Pikachu'))"

"""

import pandas as pd
import numpy as np

# Load Excel file with multiple sheets
xls = pd.read_excel('pokemonStats.xlsx', sheet_name=['Sheet1', 'Sheet2'])

# Access individual sheets
pokemon_df = xls['Sheet1']
type_chart_df = xls['Sheet2']

# Function to get effectiveness lists without using .query()
def get_effectiveness(types):

    if len(types) == 2 and pd.notna(types[1]):
        # Both types present
        most_eff_mask = (type_chart_df[types[0]] == 2) & (type_chart_df[types[1]] == 2)
        super_eff_mask = (
            ((type_chart_df[types[0]] == 2) & (type_chart_df[types[1]] == 1)) |
            ((type_chart_df[types[0]] == 1) & (type_chart_df[types[1]] == 2))
        )
        most_eff = type_chart_df.loc[most_eff_mask, 'Type'].to_numpy()
        super_eff = type_chart_df.loc[super_eff_mask, 'Type'].to_numpy()
        return most_eff, super_eff
    else:
        # Single type Pokémon
        most_eff_mask = type_chart_df[types[0]] == 2
        most_eff = type_chart_df.loc[most_eff_mask, 'Type'].to_numpy()
        return most_eff, None

def findMostEffective(pokemon_name):
    # Find the row index of the Pokémon
    pokemon_row_idx = pokemon_df.index[pokemon_df['Name'] == pokemon_name][0]

    # Get the Pokémon's Type 1 and Type 2
    type1 = pokemon_df.at[pokemon_row_idx, 'Type 1']
    type2 = pokemon_df.at[pokemon_row_idx, 'Type 2']   

    # Get effectiveness lists
    most_effective, super_effective = get_effectiveness([type1, type2])

    # If no most effective types, fallback to super effective
    if most_effective.size == 0 and super_effective is not None:
        most_effective = super_effective
        super_effective = None  # No need for further filtering

    # Print Pokémon types and effectiveness
    if pd.notna(type2):
        print(f"This Pokémon is {type1} and {type2}")
        print("Most effective against:", most_effective)
        if super_effective is not None:
            print("Super effective against:", super_effective)
    else:
        print(type1)
        print("Most effective against:", most_effective)

    # Filter capable Pokémon based on effectiveness
    if super_effective is not None:
        capable_mask = (
            (pokemon_df['Type 1'].isin(most_effective)) &
            ((pokemon_df['Type 2'].isin(super_effective)) | pokemon_df['Type 2'].isna())
        )
    else:
        capable_mask = (
            (pokemon_df['Type 1'].isin(most_effective)) &
            ((pokemon_df['Type 2'].isin(most_effective)) | pokemon_df['Type 2'].isna())
        )

    return pokemon_df[capable_mask]

    

if __name__ == "__main__":
    # Print the top 10 capable Pokémon by Attack
    pokemon = 'Garchomp'
    top_10 = findMostEffective(pokemon).nlargest(10, 'Attack')['Name'].to_numpy()
    print("Top 10 capable Pokémon by Attack:")
    print(top_10)
    