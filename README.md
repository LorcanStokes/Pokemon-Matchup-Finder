The goal of this project was to utilize data analytics libraries to sort through all pokémon and Pokémon types to find the bet pokemon that would be most effective against the target Pokémon.
All Pokémon from Gen.1 to Gen.9 (the most recent generation at the time of writing this code) are included in the .xlsx file and which types are least, normal, super and most effective against all types.

There are 2 runnable versions of the code:
1. Run as 'effective_finder' and change the target Pokémon ion the main or run intermainl and call the function findMostEffective('Pikachu').
2. Run 'pokemonApp' whci opens flask and a UI in browser to input the target Pokémon and recieve 10 most effective Pokémon.

Requirements:
numpy==1.24.4
pandas==1.15.0
flask==1.1.1
