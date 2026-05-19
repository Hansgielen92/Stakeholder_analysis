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

base_path = Path.cwd() #Path.cwd() geeft de huidige werkmap terug. Base_path is die map plus de mapnaam
print(f"The path is: {base_path}")

def calculate_profile_score(df, attribute_prefix):
   return (df[f'{attribute_prefix}_min'] + 2 * df[f'{attribute_prefix}_mean'] + df[f'{attribute_prefix}_max']) / 4
  

def fuzzy_synthesize(folder_name = 'data_demo'):
   
   script_dir = Path(__file__).resolve().parent
   base_path = script_dir/folder_name #Path.cwd() geeft de huidige werkmap terug. Base_path is die map plus de mapnaam
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

#Creëren van Universele sets voor de attributen

x_power = np.arange(0,3.1,0.1)
x_legitimacy = np.arange(0,3.1,0.1)
x_urgency = np.arange(0,3.1,0.1)
x_salience = np.arange(0,3.1,0.1)

#Maken van fuzzy membershipfuncties voor elk attribuut

power_low = fuzz.trapmf(x_power, list(ATTRIBUTE_CONFIG['power']['Low']))
power_high = fuzz.trapmf(x_power, list(ATTRIBUTE_CONFIG['power']['High']))
legitimacy_low = fuzz.trapmf(x_legitimacy, list(ATTRIBUTE_CONFIG['legitimacy']['Absent']))
legitimacy_high = fuzz.trapmf(x_legitimacy, list(ATTRIBUTE_CONFIG['legitimacy']['Present']))
urgency_low = fuzz.trapmf(x_urgency, list(ATTRIBUTE_CONFIG['urgency']['Low']))
urgency_high = fuzz.trapmf(x_urgency, list(ATTRIBUTE_CONFIG['urgency']['High']))
salience_none = fuzz.trapmf(x_salience, list(ATTRIBUTE_CONFIG['salience']['None']))
salience_low = fuzz.trapmf(x_salience, list(ATTRIBUTE_CONFIG['salience']['Low']))
salience_moderate = fuzz.trapmf(x_salience, list(ATTRIBUTE_CONFIG['salience']['Moderate']))
salience_high = fuzz.trapmf(x_salience, list(ATTRIBUTE_CONFIG['salience']['High']))

#plotten van de membershipfuncties
fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4, figsize=(8, 9))
ax0.plot(x_power, power_low, 'b', linewidth=1.5, label='Low')
ax0.plot(x_power, power_high, 'g', linewidth=1.5, label='High')

ax0.set_title('Power')
ax0.legend()

ax1.plot(x_legitimacy, legitimacy_low, 'b', linewidth=1.5, label='Absent')
ax1.plot(x_legitimacy, legitimacy_high, 'g', linewidth=1.5, label='Present')

ax1.set_title('Legitimacy')
ax1.legend()

ax2.plot(x_urgency, urgency_low, 'b', linewidth=1.5, label='Low')
ax2.plot(x_urgency, urgency_high, 'g', linewidth=1.5, label='High')

ax2.set_title('Urgency')
ax2.legend()

ax3.plot(x_salience, salience_low, 'b', linewidth=1.5, label='Low')
ax3.plot(x_salience, salience_moderate, 'y', linewidth=1.5, label='Moderate')
ax3.plot(x_salience, salience_high, 'g', linewidth=1.5, label='High')

ax3.set_title('Salience')
ax3.legend()

plt.tight_layout()
plt.savefig('output.png', dpi=150, bbox_inches='tight')
plt.close()

#toepassen van de functies op data
df['power_low']       = df['profile_score_power'].apply(lambda v: fuzz.interp_membership(x_power, power_low, v))
df['power_high']      = df['profile_score_power'].apply(lambda v: fuzz.interp_membership(x_power, power_high, v))
df['legitimacy_absent']  = df['profile_score_legitimacy'].apply(lambda v: fuzz.interp_membership(x_legitimacy, legitimacy_low, v))
df['legitimacy_present'] = df['profile_score_legitimacy'].apply(lambda v: fuzz.interp_membership(x_legitimacy, legitimacy_high, v))
df['urgency_low']     = df['profile_score_urgency'].apply(lambda v: fuzz.interp_membership(x_urgency, urgency_low, v))
df['urgency_high']    = df['profile_score_urgency'].apply(lambda v: fuzz.interp_membership(x_urgency, urgency_high, v))


#definiëren van de fuzzy regels

final_scores = []
dominant_rules = []

for i, row in df.iterrows():
    r_dormant = min(row['power_high'], row['legitimacy_absent'], row['urgency_low'])
    r_discretionary = min(row['power_low'], row['legitimacy_present'], row['urgency_low'])
    r_demanding = min(row['power_low'], row['legitimacy_absent'], row['urgency_high'])
    r_dominant = min(row['power_high'], row['legitimacy_present'], row['urgency_low'])
    r_dangerous = min(row['power_high'], row['legitimacy_absent'], row['urgency_high'])
    r_dependent = min(row['power_low'], row['legitimacy_present'], row['urgency_high'])
    r_definitive = min(row['power_high'], row['legitimacy_present'], row['urgency_high'])
    r_none = min(row['power_low'], row['legitimacy_absent'], row['urgency_low'])

    #activeren van regels
    active_none = r_none
    active_low = max(r_dormant, r_discretionary, r_demanding)
    active_moderate = max(r_dominant, r_dangerous, r_dependent)
    active_high = r_definitive


    #clipping van de resultaten
    act_salience_none = np.fmin(active_none, salience_none)
    act_salience_low = np.fmin(active_low, salience_low)
    act_salience_moderate = np.fmin(active_moderate, salience_moderate)
    act_salience_high = np.fmin(active_high, salience_high)

    

    #aggregatie van de resultaten
    aggregated = np.fmax(act_salience_none, np.fmax(act_salience_low, np.fmax(act_salience_moderate, act_salience_high)))

    #defuzzificatie van de resultaten
    if np.max(aggregated) > 0:
        salience_score = fuzz.defuzz(x_salience, aggregated, 'centroid')
        salience_activation = fuzz.interp_membership(x_salience, aggregated, salience_score)
    else:
        salience_score = 0
        salience_activation = 0
    final_scores.append(salience_score)
    
    all_rules = {
        'Dormant': r_dormant,
        'Discretionary': r_discretionary,
        'Demanding': r_demanding,
        'Dominant': r_dominant,
        'Dangerous': r_dangerous,
        'Dependent': r_dependent,
        'Definitive': r_definitive,
        'None': r_none
    }
    dominant_rule = max(all_rules, key=all_rules.get)
    dominant_rules.append(dominant_rule)

df['final_salience_score'] = final_scores
df['dominant_rule'] = dominant_rules

#schrijven van pdf met resultaten per stakeholder en maakt hier een export van
def write_results_to_pdf(df, filename='demo_stakeholder_analysis_results.pdf'):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for index, row in df.iterrows():
        pdf.cell(200, 10, txt=f"Stakeholder: {row['stakeholder']}", ln=True)
        pdf.cell(200, 10, txt=f"Final Salience Score: {row['final_salience_score']:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Dominant Rule: {row['dominant_rule']}", ln=True)
        pdf.cell(200, 10, txt="-----------------------------", ln=True)

    pdf.output(filename)

write_results_to_pdf(df)
