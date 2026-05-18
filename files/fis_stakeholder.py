import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
from pathlib import Path
import os
import glob
import skfuzzy as fuzz

def calculate_profile_score(df, attribute_prefix):
   return (df[f'{attribute_prefix}_min'] + 2 * df[f'{attribute_prefix}_mean'] + df[f'{attribute_prefix}_max']) / 4
  

def fuzzy_synthesize(folder_name = 'data_2'):
   base_path = Path.cwd()/folder_name #Path.cwd() geeft de huidige werkmap terug. Base_path is die map plus de mapnaam
   pattern = '*.csv'
   csv_files = list(base_path.glob(pattern))

   if not csv_files: #als er geen csv-bestanden zijn gevonden, geef een foutmelding
     raise FileNotFoundError(f"No CSV files found in the folder: {base_path}")
   
   all_data=[pd.read_csv(file, sep=',', encoding='utf-8') for file in csv_files]
   df = pd.concat(all_data, ignore_index=True)

   #Definiëren van de attributen per vraag
   df['power_score'] = df[['vraag_1', 'vraag_2', 'vraag_3']].mean(axis=1)
   df['legitimacy_score'] = df[['vraag_4', 'vraag_5', 'vraag_6']].mean(axis=1)
   df['urgency_score'] = df[['vraag_7', 'vraag_8', 'vraag_9']].mean(axis=1)


   #Aggregeren van de score per attribuut per stakeholder (stap 2 van Poplawska)
   synthesis = df.groupby('stakeholder').agg(
       #power attribuut
       power_mean = ('power_score', 'mean'),
       power_max = ('power_score', 'max'),
       power_min = ('power_score', 'min'),

       #legitimacy attribuut
       legitimacy_mean = ('legitimacy_score', 'mean'),
       legitimacy_max = ('legitimacy_score', 'max'),
       legitimacy_min = ('legitimacy_score', 'min'),

       #urgency attribuut
       urgency_mean = ('urgency_score', 'mean'),
       urgency_max = ('urgency_score', 'max'),
       urgency_min = ('urgency_score', 'min')
   ).reset_index()

   #Berekenen van de salience scores (stap 3 van Poplawska)

   synthesis['salience_mean'] = synthesis[['power_mean', 'legitimacy_mean', 'urgency_mean']].mean(axis=1)
   synthesis['salience_max'] = synthesis[['power_max', 'legitimacy_max', 'urgency_max']].max(axis=1)
   synthesis['salience_min'] = synthesis[['power_min', 'legitimacy_min', 'urgency_min']].min(axis=1)

   synthesis['profile_score_power'] = calculate_profile_score(synthesis, 'power')
   synthesis['profile_score_legitimacy'] = calculate_profile_score(synthesis, 'legitimacy')
   synthesis['profile_score_urgency'] = calculate_profile_score(synthesis, 'urgency')
   synthesis['profile_score_salience'] = calculate_profile_score(synthesis, 'salience')
  
   
   return synthesis

#definiëren van de fuzzy sets voor elk attribuut
ATTRIBUTE_CONFIG = {
    'power': {
        'Low': [0, 0, 0.6, 1.2],    # Example: boundaries for Power
        'High': [0.6, 1.2, 3, 3]
    },
    'urgency': {
        'Low': [0, 0, 0.6, 1.2],    # Often the same as Power in this paper
        'High': [0.6, 1.2, 3, 3]
    },
    'legitimacy': {
        'Absent': [0, 0, 0, 0], # Legitimacy gebruikt absent/present
        'Present': [0, 0.6, 2.4, 3]
    },
    'salience': {                   # Final Salience heeft vier categorieën
        'None': [0,0,0,0],
        'Low': [0, 0, 0.6, 1.2],
        'Moderate': [0.6, 1.2, 1.8, 2.4],
        'High': [1.8, 2.4, 3, 3]
    }
}



df = fuzzy_synthesize()

