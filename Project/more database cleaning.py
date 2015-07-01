# Export from IPython Notebook
import pandas as pd

# Load instagram API data
# Paris, July 2014
paris_csv = pd.read_csv('insta_paris_July_lan.csv',encoding='utf-8') 
paris_csv = paris_csv.drop_duplicates()
paris_lan.rename(columns={paris_lan.columns[0]:'language'}, inplace=True)
paris_lan.rename(columns={paris_lan.columns[1]:'prob'}, inplace=True)

# Manually (!) corrected and standardized bugs in locations names
paris_lan.loc[paris_lan.locName == 'Galeries Lafayette Paris', 'locName'] = 'Galeries Lafayette'
paris_lan.loc[paris_lan.locName == 'La Machine du Moulin Rouge', 'locName'] = 'Moulin Rouge'
paris_lan.loc[paris_lan.locName == 'Le Moulin Rouge (Officiel)', 'locName'] = 'Moulin Rouge'
paris_lan.loc[paris_lan.locName == 'paris', 'locName'] = 'Paris, France'
paris_lan.loc[paris_lan.locName == 'Paris', 'locName'] = 'Paris, France'
paris_lan.loc[paris_lan.locName == 'Paris France', 'locName'] = 'Paris, France'
paris_lan.loc[paris_lan.locName == 'Eiffel Tower Paris France', 'locName'] = 'Eiffel Tower'
paris_lan.loc[paris_lan.locName == 'La Tour Eiffel, Paris', 'locName'] = 'Eiffel Tower'
paris_lan.loc[paris_lan.locName == 'Eiffel Tower Paris', 'locName'] = 'Eiffel Tower'
paris_lan.loc[paris_lan.locName == 'Champ De Mars , Tour Eiffel', 'locName'] = 'Eiffel Tower'
paris_lan.loc[paris_lan.locName == 'Tour Eiffel', 'locName'] = 'Eiffel Tower'
paris_lan.loc[paris_lan.locName == 'Musée Du Louvre, París', 'locName'] = 'Musee Du Louvre'
paris_lan.loc[paris_lan.locName == 'Louvre Museum Of Art, Paris', 'locName'] = 'Musee Du Louvre'
paris_lan.loc[paris_lan.locName == 'Louvre', 'locName'] = 'Musee Du Louvre'
paris_lan.loc[paris_lan.locName == 'Musée Du Louvre', 'locName'] = 'Musee Du Louvre'
paris_lan.loc[paris_lan.locName == 'Pont Des Arts - Paris', 'locName'] = 'Pont Des Arts'
paris_lan.loc[paris_lan.locName == 'Arc De Triomphe', 'locName'] = 'Arc de Triumph, Paris'
paris_lan.loc[paris_lan.locName == 'Arc de Triomphe du Carrousel', 'locName'] = 'Arc de Triumph, Paris'
paris_lan.loc[paris_lan.locName == 'Le Marais, Paris', 'locName'] = 'Quartier Le Marais, Paris'
paris_lan.loc[paris_lan.locName == 'Tuileries Garden-Jardin Des Tuileries', 'locName'] = 'Jardin des Tuileries'
paris_lan.loc[paris_lan.locName == 'Tuileries', 'locName'] = 'Jardin des Tuileries'
paris_lan.loc[paris_lan.locName == 'Jardins du Luxembourg, Paris', 'locName'] = 'Jardin du Luxembourg'
paris_lan.loc[paris_lan.locName == "Musee d'Orsay", 'locName'] = "Musee d'Orsay (officiel)"
paris_lan.loc[paris_lan.locName == "Champs Elysees Paris", 'locName'] = "Champs-Elysees"
paris_lan.loc[paris_lan.locName == "River Seine, Paris", 'locName'] = "La Seine"
paris_lan.loc[paris_lan.locName == "Quai de Seine", 'locName'] = "La Seine"
paris_lan.loc[paris_lan.locName == "Quai de Seine", 'locName'] = "La Seine"
paris_lan.loc[paris_lan.locName == "Paris Gare du Nord", 'locName'] = "Gare du Nord Paris, Eurostar"
paris_lan.loc[paris_lan.locName == "Paris - Gare de Lyon", 'locName'] = "Paris Gare de Lyon"
paris_lan.loc[paris_lan.locName == "Hôtel de Ville, Paris", 'locName'] = "Hotel de Ville, Paris"
paris_lan.loc[paris_lan.locName == "Place de l'Hôtel-de-Ville - Esplanade de la Libération", 'locName'] = "Hotel de Ville, Paris"
paris_lan.loc[paris_lan.locName == "L'Opéra de Paris (Palais Garnier)", 'locName'] = "Palais Garnier"
paris_lan.loc[paris_lan.locName == "Palais Garnier - Opéra De Paris", 'locName'] = "Palais Garnier"
paris_lan.loc[paris_lan.locName == "Opéra Garnier", 'locName'] = "Palais Garnier"
paris_lan.loc[paris_lan.locName == 'Cathédrale Notre-Dame de Paris', 'locName'] = 'Notre-Dame De Paris'
paris_lan.loc[paris_lan.locName == 'Cathédrale Notre Dame', 'locName'] = 'Notre-Dame De Paris'
paris_lan.loc[paris_lan.locName == 'Printemps', 'locName'] = 'La Terrasse Du Printemps'
paris_lan.loc[paris_lan.locName == 'Lovers Lock Bridge', 'locName'] = 'Pont Des Arts - Love Lock Bridge'
paris_lan.loc[paris_lan.locName == 'Grand Palais', 'locName'] = 'Grand Palais Paris'
paris_lan.loc[paris_lan.locName == 'Grand Palais - Robert Mapplethorpe', 'locName'] = 'Grand Palais Paris'
paris_lan.loc[paris_lan.locName == 'Grand Palais - RMN (Officiel)', 'locName'] = 'Grand Palais Paris'
paris_lan.loc[paris_lan.locName == 'Le Grand Palais - Bill Viola', 'locName'] = 'Grand Palais Paris'
paris_lan.loc[paris_lan.locName == 'Montmartre, Paris', 'locName'] = 'Basilique Du Sacre Coeur, Montmartre'
paris_lan.loc[paris_lan.locName == 'Montmartre', 'locName'] = 'Basilique Du Sacre Coeur, Montmartre'
paris_lan.loc[paris_lan.locName == 'Basilique Du Sacré Coeur, Montmartre', 'locName'] = 'Basilique Du Sacre Coeur, Montmartre'
paris_lan.loc[paris_lan.locName == 'Basilique du Sacré-Cœur de Montmartre', 'locName'] = 'Basilique Du Sacre Coeur, Montmartre'
paris_lan.loc[paris_lan.locName == 'Champs-Élysées', 'locName'] = 'Champs-Elysees'
paris_lan.loc[paris_lan.locName == 'Petit Palais Paris 1900', 'locName'] = 'Petit Palais, musee des Beaux-arts'
paris_lan.loc[paris_lan.locName == 'Petit Palais, musée des Beaux-arts', 'locName'] = 'Petit Palais, musee des Beaux-arts'
paris_lan.loc[paris_lan.locName == 'CHANEL Boutique in Paris', 'locName'] = 'Chanel, 31 Rue Cambon'
paris_lan.loc[paris_lan.locName == 'Eiffel Tower, Paris, France', 'locName'] = 'Eiffel Tower'
paris_lan.loc[paris_lan.locName == 'Notre-Dame Cathedral', 'locName'] = 'Notre-Dame De Paris'


