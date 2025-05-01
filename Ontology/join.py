import pandas as pd

data1 = pd.read_csv('./Dataset/pokemon.csv')
data2 = pd.read_csv('./Dataset/pokemon_evolution.csv')


data1['name'] = data1['name'].str.strip().str.lower()
data2['name'] = data2['name'].str.strip().str.lower()


#print("First 5 names in data1:", data1['name'].head().tolist())
#print("First 5 names in data2:", data2['name'].head().tolist())

data2 = data2[['name', 'Evolution']]

merged_df = pd.merge(data1, data2, on='name', how='inner')
merged_df.to_csv('./Dataset/final_pokemon.csv', index=False)

print("Merged dataset saved to './Dataset/merged_pokemon.csv'")
