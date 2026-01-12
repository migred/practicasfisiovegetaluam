"""
Dashboard Completo de Prácticas de Fisiología Vegetal
Universidad Autónoma de Madrid (UAM)

5 Prácticas completas con análisis, validaciones, gráficas y PDF
"""

import gradio as gr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import tempfile
import io
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')
plt.ion()  # Activar modo interactivo para que las figuras no se cierren

# ============================================================================
# FUNCIONES MATEMÁTICAS
# ============================================================================

def sigmoid(x, xmid, scal):
    """Función sigmoide: 100 / (1 + exp(-(x - xmid) * scal))"""
    return 100 / (1 + np.exp(-(x - xmid) * scal))

def calculate_potencial_50(xmid, scal):
    """Calcula el potencial osmótico al 50% de plasmólisis"""
    return round((np.log((100 - 50) / 50) / scal) + xmid, 2)

def validate_column(df, student_col, correct_col, tolerance=0.1):
    """Valida si los cálculos del estudiante son correctos"""
    ratio = df[student_col] / df[correct_col]
    return ['✅ Correcto' if ((0.9 <= r <= 1.1) or (df[student_col].iloc[i] == 0 and df[correct_col].iloc[i] == 0)) 
            else '❌ Incorrecto' for i, r in enumerate(ratio)]

def style_dataframe(df, validation_cols=[]):
    """Aplica estilo a DataFrame con colores para validaciones"""
    def highlight_row(row):
        colors = []
        for col in df.columns:
            if col in validation_cols:
                colors.append('background-color: #d4edda' if '✅' in str(row[col]) else 'background-color: #f8d7da')
            else:
                colors.append('')
        return colors
    return df.style.apply(highlight_row, axis=1)

# ============================================================================
# PRÁCTICA 1: POTENCIAL OSMÓTICO Y HÍDRICO
# ============================================================================

def process_practica1(file_path):
    """Procesa toda la Práctica 1: sacarosa, cebolla y patata"""
    results = {}
    
    try:
        print(f"  → Leyendo Práctica 1 de: {file_path}")
        # 1. SACAROSA
        df_sac = pd.read_excel(file_path, sheet_name="Practica 1", usecols="B:C", skiprows=5, nrows=8)
        df_sac.columns = ['Concentración (M)', 'Ψ estudiante (MPa)']
        df_sac['Ψ correcto (MPa)'] = round(-df_sac['Concentración (M)'] * 0.008314 * 295, 2)
        df_sac['Validación'] = validate_column(df_sac, 'Ψ estudiante (MPa)', 'Ψ correcto (MPa)')
        results['sacarosa'] = df_sac
        print(f"  ✓ Sacarosa: {len(df_sac)} filas")
        results['sacarosa_expl'] = r"""
**Cálculo del potencial hídrico de sacarosa usando ecuación de van't Hoff:**

Para el cálculo del potencial hídrico de la solución de sacarosa utilizamos la ecuación de van't Hoff:

$$\Psi_{s}=-RTiCs$$

Asumiendo que obtenemos un valor X al aplicar la ecuación, para la conversión de las unidades debería seguir los siguientes pasos:

$$X\: \frac{J}{{\color{red}{K}} \cdot {\color{red} {mol}}} \times {{\color{red}{K}}} \times {\frac{\color{red} {mol}}{L}} \Rightarrow X\: \frac{J}{{\color{red} {L}}} \times {\frac{1000\:{\color{red} {L}}}{m^{3}}}\Rightarrow$$

$$\Rightarrow 1000X\: \frac{J}{m^{3}}\Rightarrow 1000X\: {\color{red} {Pa}} \times{\frac{MPa}{10^{6}\color{red} {Pa}}}$$

Por lo tanto la fórmula final podríamos reflejarla como:

$$\Psi_{w}=-\frac{X}{1000} \text{ MPa}$$
"""
        
        # 2. CEBOLLA
        df_onion = pd.read_excel(file_path, sheet_name="Practica 1", usecols="B:E", skiprows=17, nrows=7, header=None)
        df_onion.columns = ['Tubos', 'Concentración (M)', 'Ψπ (MPa)', '% plasmólisis']
        df_onion['Ψπ (MPa)'] = pd.to_numeric(df_onion['Ψπ (MPa)'], errors='coerce')
        df_onion['% plasmólisis'] = pd.to_numeric(df_onion['% plasmólisis'], errors='coerce')
        df_onion = df_onion.dropna()
        
        # Validar plasmólisis decreciente
        plasmo_val = []
        for i in range(len(df_onion)):
            if i == 0:
                plasmo_val.append('✅' if df_onion['% plasmólisis'].iloc[i] >= df_onion['% plasmólisis'].iloc[i+1] else '❌')
            elif i == len(df_onion)-1:
                plasmo_val.append('✅' if df_onion['% plasmólisis'].iloc[i] <= df_onion['% plasmólisis'].iloc[i-1] else '❌')
            else:
                plasmo_val.append('✅' if (df_onion['% plasmólisis'].iloc[i] <= df_onion['% plasmólisis'].iloc[i-1] and 
                                          df_onion['% plasmólisis'].iloc[i] >= df_onion['% plasmólisis'].iloc[i+1]) else '❌')
        df_onion['Val. Orden'] = plasmo_val
        
        # Modelo sigmoide
        try:
            x = df_onion['Ψπ (MPa)'].values
            y = df_onion['% plasmólisis'].values
            params, _ = curve_fit(sigmoid, x, y, p0=[np.median(x), 1], maxfev=5000)
            xmid, scal = params
            potencial_osm = calculate_potencial_50(xmid, scal)
            
            fig_onion, ax = plt.subplots(figsize=(10, 7))
            ax.scatter(x, y, s=80, alpha=0.7, color='#2ecc71', edgecolors='black', linewidths=2, label='Datos', zorder=3)
            x_range = np.linspace(x.min(), x.max(), 200)
            ax.plot(x_range, sigmoid(x_range, xmid, scal), 'b-', linewidth=3, label='Modelo sigmoide', zorder=2)
            ax.axhline(y=50, color='gray', linestyle='--', linewidth=2, alpha=0.6, label='50% plasmólisis', zorder=1)
            ax.axvline(x=potencial_osm, color='red', linestyle=':', linewidth=2.5, alpha=0.8, label=f'Ψπ = {potencial_osm} MPa', zorder=1)
            ax.set_xlabel('Potencial osmótico (MPa)', fontsize=14, fontweight='bold')
            ax.set_ylabel('Porcentaje de plasmólisis (%)', fontsize=14, fontweight='bold')
            ax.set_title('Plasmólisis en células de cebolla', fontsize=16, fontweight='bold', pad=20)
            ax.legend(fontsize=12, frameon=True, shadow=True)
            ax.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            plt.draw()  # Dibujar la figura
            
            results['onion'] = df_onion
            results['onion_fig'] = fig_onion
            results['onion_pot'] = potencial_osm
            print(f"  ✓ Cebolla: {len(df_onion)} filas, potencial={potencial_osm} MPa")
            results['onion_expl'] = f"""
**Análisis de Plasmólisis:**

A la hora de revisar los resultados, hay que cerciorarse de que el porcentaje de células plasmolizadas **disminuya a la par que se reduce la concentración de sacarosa en el medio**. 

En una solución hipertónica como la del tubo 1, el potencial osmótico de las células será superior al del medio y por tanto perderán agua conduciendo a la plasmólisis. Si se disminuye la concentración de sacarosa en el medio, su potencial osmótico irá aumentando hasta el punto en el que será hipotónica respecto al tejido y las moléculas de agua pasarán a las células provocando la turgencia. 

Por lo tanto, para estimar el potencial osmótico medio del tejido de epidermis de cebolla observamos el porcentaje de células plasmolizadas y ajustamos los puntos a una **curva sigmoide**.

El valor del potencial osmótico medio corresponderá al punto en el que se observa que el 50% de las células han plasmolizado.

**Por lo tanto, el valor de Potencial osmótico medio se puede estimar en este caso en** <span style='color:red; font-weight:bold;'>{potencial_osm} MPa</span>

**Parámetros del modelo:** xmid = {round(xmid, 3)}, scal = {round(scal, 3)}
"""
        except Exception as e:
            results['onion_error'] = f"Error en modelo sigmoide: {e}"
        
        # 3. PATATA
        df_potato = pd.read_excel(file_path, sheet_name="Practica 1", usecols="B:G", skiprows=37, nrows=7, header=None)
        df_potato.columns = ['Tubos', 'Concentración (M)', 'Ψw (MPa)', 'Peso inicial (g)', 'Peso final (g)', '% Var estudiante']
        df_potato['% Var correcto'] = round((df_potato['Peso final (g)'] - df_potato['Peso inicial (g)']) / df_potato['Peso inicial (g)'] * 100, 2)
        df_potato['Validación'] = validate_column(df_potato, '% Var estudiante', '% Var correcto')
        
        # Regresión lineal
        x = df_potato['Ψw (MPa)'].values
        y = df_potato['% Var estudiante'].values
        slope, intercept, r_value, _, _ = linregress(x, y)
        hydric_pot = round(-intercept / slope, 2)
        
        fig_potato, ax = plt.subplots(figsize=(10, 7))
        ax.scatter(x, y, s=80, alpha=0.7, color='#e74c3c', edgecolors='black', linewidths=2, label='Datos', zorder=3)
        ax.plot(x, slope * x + intercept, 'b-', linewidth=3, label='Regresión lineal', zorder=2)
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=2, alpha=0.6, zorder=1)
        ax.axvline(x=hydric_pot, color='red', linestyle=':', linewidth=2.5, alpha=0.8, label=f'Ψw = {hydric_pot} MPa', zorder=1)
        ax.set_xlabel('Potencial hídrico (MPa)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Variación de peso (%)', fontsize=14, fontweight='bold')
        ax.set_title('Potencial hídrico en patata', fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=12, frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.draw()  # Dibujar la figura
        
        results['potato'] = df_potato
        results['potato_fig'] = fig_potato
        results['potato_pot'] = hydric_pot
        print(f"  ✓ Patata: {len(df_potato)} filas, potencial={hydric_pot} MPa")
        results['potato_expl'] = f"""
**Cálculo del Potencial Hídrico:**

Para el cálculo del potencial hídrico del tubérculo de patata comparamos la variación de peso (en porcentaje) del tejido de patata frente al Potencial hídrico de la solución de sacarosa.

Antes hemos de cerciorarnos que hemos calculado bien el porcentaje de variación de peso:

$$\\frac{{(\\text{{Peso final}} - \\text{{Peso inicial}})}}{{\\text{{Peso inicial}}}} \\times 100$$

Para calcular el Potencial hídrico del tejido de patata, hemos de asumir que la relación entre el Potencial hídrico y la variación de peso es lineal:

$$\\% \\text{{ Variación de peso}} = a \\times \\text{{Potencial hídrico}} + b$$

Si asumimos que el Potencial hídrico del tejido es aquel valor de Potencial hídrico que hace que la variación de peso sea 0, podemos despejar la ecuación anterior para encontrar el valor de Potencial hídrico:

$$0 = a \\times \\text{{Potencial hídrico}} + b$$

$$\\text{{Potencial hídrico}} = -\\frac{{b}}{{a}}$$

Para encontrar los valores de a y b, podemos usar el método de **mínimos cuadrados**, que nos permitirá encontrar la recta que mejor se ajusta a los datos.

Al aplicarlos obtenemos un valor de pendiente igual a <span style='color:red; font-weight:bold;'>{round(slope, 3)}</span>, y un valor de ordenada de origen igual a <span style='color:red; font-weight:bold;'>{round(intercept, 3)}</span>.

Despejando obtenemos que el **Potencial hídrico del tejido es igual a** <span style='color:red; font-weight:bold;'>{hydric_pot} MPa</span>
"""
        
    except Exception as e:
        results['error'] = f"Error procesando Práctica 1: {e}"
    
    return results

# ============================================================================
# PRÁCTICA 2: AUXINAS Y ESTRÉS SALINO
# ============================================================================

def process_practica2(file_path):
    """Procesa Práctica 2: maíz (auxina) y guisante (NaCl)"""
    results = {}
    
    try:
        print(f"  → Leyendo Práctica 2 de: {file_path}")
        
        # 1. MAÍZ - AUXINA (B8:F10 en R, equivale a skiprows=7, nrows=2 - solo datos válidos)
        # En R se lee horizontal y se transpone, aquí leemos directamente
        try:
            df_corn = pd.read_excel(file_path, sheet_name="Practica 2", usecols="B:F", skiprows=7, nrows=2)
            print(f"  → Maíz leído: {df_corn.shape}")
            # Transponer: las columnas son tratamientos
            df_corn_t = df_corn.T
            df_corn_t.columns = df_corn_t.iloc[0]
            df_corn_t = df_corn_t[1:].reset_index()
            df_corn_t.columns = ['Tratamiento', 'Media longitud (mm)', 'Variación(%) estudiante']
            df_corn_t['Variación(%) correcto'] = round((df_corn_t['Media longitud (mm)'].astype(float) - 10) / 10 * 100, 2)
            df_corn_t['Validación'] = validate_column(df_corn_t, 'Variación(%) estudiante', 'Variación(%) correcto')
            
            fig_corn, ax = plt.subplots(figsize=(10, 7))
            x_pos = np.arange(len(df_corn_t))
            bars = ax.bar(x_pos, df_corn_t['Variación(%) correcto'], color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], edgecolor='black', linewidth=1.0)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(df_corn_t['Tratamiento'], fontsize=12, rotation=15, ha='right')
            ax.set_xlabel('Tratamiento', fontsize=14, fontweight='bold')
            ax.set_ylabel('Variación (%)', fontsize=14, fontweight='bold')
            ax.set_title('Efecto de auxina en coleóptilos de maíz', fontsize=16, fontweight='bold', pad=20)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
            plt.tight_layout()
            plt.draw()  # Dibujar la figura
            
            results['corn'] = df_corn_t
            results['corn_fig'] = fig_corn
            print(f"  ✓ Maíz: {len(df_corn_t)} filas")
        except Exception as e:
            error_msg = f"Error en Maíz: {str(e)}"
            print(f"  ✗ {error_msg}")
            results['corn'] = pd.DataFrame()
            results['corn_fig'] = None
            results['corn_error'] = error_msg
        
        results['corn_expl'] = r"""
**Efecto de Auxina en Coleóptilos de Maíz:**

Para el cálculo de la variación de longitud de coleóptilo de maíz, hemos de comparar la longitud media de coleóptilo de maíz en diferentes tratamientos a las 24h respecto a los 10 mm iniciales.

$$\text{Variación} (\%) = \frac{\text{Longitud media} - 10}{10} \times 100$$

Una vez calculado la variación de longitud en los distintos tratamientos de Auxina tenemos que prestar atención a los valores obtenidos:

- ¿Hay diferencias entre tratamientos?
- ¿Se elonga el coleóptilo de maíz según incrementamos la concentración de Auxina o llegado un punto se observan alteraciones?
"""
        
        # 2. GUISANTE - ESTRÉS SALINO (H8:K14 en R, equivale a skiprows=7, nrows=7)
        # En R también se transpone
        try:
            df_pea = pd.read_excel(file_path, sheet_name="Practica 2", usecols="H:K", skiprows=7, nrows=7)
            print(f"  → Guisante leído: {df_pea.shape}")
            # La primera columna contiene los nombres de tratamiento
            df_pea_t = df_pea.T
            df_pea_t.columns = df_pea_t.iloc[0]
            df_pea_t = df_pea_t[1:].reset_index(drop=True)
            df_pea_t['Concentración NaCl'] = df_pea_t.index.astype(str)
            df_pea_t = df_pea_t[['Concentración NaCl'] + [col for col in df_pea_t.columns if col != 'Concentración NaCl']]
            
            # Calcular variación de peso
            peso_seco = df_pea_t['Peso seco (g)'].astype(float)
            peso_humedo = df_pea_t['Peso húmedo (g)'].astype(float)
            df_pea_t['% Var correcto'] = round((peso_humedo - peso_seco) / peso_seco * 100, 2)
            
            # Gráfica de variación de peso
            fig_pea1, ax = plt.subplots(figsize=(8, 6))
            ax.bar(range(len(df_pea_t)), df_pea_t['% Var correcto'], color='#16a085', edgecolor='black', linewidth=1.0)
            ax.set_xticks(range(len(df_pea_t)))
            ax.set_xticklabels(df_pea_t['Concentración NaCl'], fontsize=11, rotation=45, ha='right')
            ax.set_xlabel('Concentración NaCl', fontsize=13, fontweight='bold')
            ax.set_ylabel('Variación peso (%)', fontsize=13, fontweight='bold')
            ax.set_title('Variación de peso en guisantes', fontsize=15, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.draw()  # Dibujar la figura
            
            # Gráfica de metabolismo (NBT, TFT)
            fig_pea2, ax = plt.subplots(figsize=(10, 6))
            x_pos = np.arange(len(df_pea_t))
            width = 0.25
            try:
                ax.bar(x_pos - width, df_pea_t['% embriones TFT'].astype(float), width, label='TFT', color='#3498db', edgecolor='black')
                ax.bar(x_pos, df_pea_t['% cotiledones NBT+'].astype(float), width, label='NBT+', color='#f39c12', edgecolor='black')
                ax.bar(x_pos + width, df_pea_t['% cotiledones NBT++'].astype(float), width, label='NBT++', color='#e74c3c', edgecolor='black')
                ax.set_xticks(x_pos)
                ax.set_xticklabels(df_pea_t['Concentración NaCl'], fontsize=11, rotation=45, ha='right')
                ax.set_xlabel('Concentración NaCl', fontsize=13, fontweight='bold')
                ax.set_ylabel('Porcentaje (%)', fontsize=13, fontweight='bold')
                ax.set_title('Actividad metabólica en guisantes', fontsize=15, fontweight='bold')
                ax.legend(fontsize=11)
                ax.grid(axis='y', alpha=0.3)
                plt.tight_layout()
                plt.draw()  # Dibujar la figura
            except:
                pass
            
            results['pea'] = df_pea_t
            results['pea_fig1'] = fig_pea1
            results['pea_fig2'] = fig_pea2
            print(f"  ✓ Guisante: {len(df_pea_t)} filas")
        except Exception as e:
            error_msg = f"Error en Guisante: {str(e)}"
            print(f"  ✗ {error_msg}")
            results['pea'] = pd.DataFrame()
            results['pea_fig1'] = None
            results['pea_fig2'] = None
            results['pea_error'] = error_msg
        
        results['pea_expl'] = r"""
**Influencia del Estrés Salino en Guisantes:**

Para el cálculo de la variación peso de los guisantes, hemos de comparar el peso húmedo de las semillas de guisante tras 24h de tratamiento frente al peso seco de las semillas antes del tratamiento.

$$\text{Variación} (\%) = \frac{\text{Peso húmedo} - \text{Peso seco}}{\text{Peso seco}} \times 100$$

**Preguntas clave:**
- ¿El estrés salino afecta a la hidratación de las semillas? ¿A qué se puede deber?
- Respecto a la viabilidad de las semillas, ¿hay alguna alteración en la actividad metabólica?
- ¿Has observado acumulación de especies reactivas de oxígeno (ROS)?
- ¿Qué reactivo nos permitía detectar dichos parámetros?
"""
        
    except Exception as e:
        results['error'] = f"Error procesando Práctica 2: {e}"
    
    return results

# ============================================================================
# PRÁCTICA 3: PIGMENTOS
# ============================================================================

def process_practica3(file_path):
    """Procesa Práctica 3: clorofilas y pigmentos"""
    results = {}
    
    try:
        # 1. CLOROFILA
        abs_val = pd.read_excel(file_path, sheet_name="Practica 3", usecols="G", skiprows=5, nrows=1, header=None).iloc[0, 0]
        conc_student = pd.read_excel(file_path, sheet_name="Practica 3", usecols="G", skiprows=7, nrows=1, header=None).iloc[0, 0]
        conc_g_student = pd.read_excel(file_path, sheet_name="Practica 3", usecols="G", skiprows=9, nrows=1, header=None).iloc[0, 0]
        
        conc_corr = round(abs_val / 76.07 * 50, 2)
        conc_g_corr = round(conc_corr * 8 / 4, 2)
        
        df_clor = pd.DataFrame({
            'Parámetro': ['ABS', 'Chla mg/mL', 'Chla mg/g'],
            'Estudiante': [abs_val, conc_student, conc_g_student],
            'Correcto': [abs_val, conc_corr, conc_g_corr]
        })
        df_clor['Validación'] = validate_column(df_clor, 'Estudiante', 'Correcto')
        
        results['clorofila'] = df_clor
        results['clor_expl'] = rf"""
**Determinación de la concentración de Chl a en extracto etanólico de espinaca:**

Para el cálculo de la concentración de clorofila, se ha de tener en cuenta que la clorofila a tiene un coeficiente de extinción molar de 76.07 mL/(mg · cm). 

Si aplicamos la ecuación de Lambert Beer:

$$\text{{Chla Determinada}} (\text{{mg/mL}}) = \frac{{\text{{ABS}}}}{{76.07}}$$

Hemos hecho una dilución 1:50 de la muestra, por lo que la concentración de clorofila en la muestra original es:

$$\text{{Chla Extracto}} (\text{{mg/mL}}) = \text{{Chla Determinada}} (\text{{mg/mL}}) \times 50$$

Para calcular la concentración de clorofila respecto a g de espinaca hemos de tener en cuenta de que hemos triturado 4 g de hoja en 8 mL de extracto:

$$\text{{Chla}} (\text{{mg/g}}) = \frac{{\text{{mg Chla}}}}{{\text{{mL Extracto}}}} \times \frac{{8 \text{{ mL Extracto}}}}{{4 \text{{ g Espinaca}}}}$$

**Resultados obtenidos:** {conc_corr} mg/mL, {conc_g_corr} mg/g
"""
        
        # 2. CROMATOGRAFÍA (B16:E22 en R, equivale a skiprows=15, nrows=6 - solo datos válidos)
        try:
            df_croma = pd.read_excel(file_path, sheet_name="Practica 3", usecols="B:E", skiprows=15, nrows=6)
            print(f"  → Cromatografía leída: {df_croma.shape}")
            df_croma.columns = ['Banda', 'Distancia pigmento', 'Distancia disolvente', 'Rf']
            
            # Añadir columna Pigmento si no existe
            if len(df_croma.columns) < 5:
                df_croma['Pigmento'] = [''] * len(df_croma)
            else:
                df_croma.columns = ['Banda', 'Distancia pigmento', 'Distancia disolvente', 'Rf', 'Pigmento']
            
            # Validar Rf decreciente
            rf_correcto = df_croma['Rf'].iloc[0] == 1 and all(np.diff(df_croma['Rf']) < 0)
            df_croma['Val. Rf'] = '✅ Correcto' if rf_correcto else '❌ Incorrecto'
            
            # Validar pigmentos (solo los que existen)
            pigs_correct = ['β-caroteno', 'Clorofila a', 'Clorofila b', 'Luteina', 'Violaxantina', 'Neoxantina'][:len(df_croma)]
            df_croma['Val. Pigmento'] = ['✅' if df_croma['Pigmento'].iloc[i] == pigs_correct[i] else '❌' for i in range(len(df_croma))]
            
            results['cromatografia'] = df_croma
            print(f"  ✓ Cromatografía: {len(df_croma)} filas")
        except Exception as e:
            error_msg = f"Error en Cromatografía: {str(e)}"
            print(f"  ✗ {error_msg}")
            results['cromatografia'] = pd.DataFrame()
            results['croma_error'] = error_msg
        
        results['croma_expl'] = r"""
**Caracterización de Pigmentos - Cromatografía:**

A la hora de determinar la identidad de los pigmentos hay que tener en cuenta dos factores: su apolaridad relativa determinada en este caso por el valor de Rf y sus máximos de absorción. 

Para la determinación de cada Rf hay que aplicar la siguiente fórmula:

$$R_f = \frac{\text{Distancia recorrida por el pigmento}}{\text{Distancia recorrida por el disolvente}}$$

El pigmento **más apolar** es el que se mueve más con el disolvente (banda 1) y el **más polar** el que se queda más cerca del punto de aplicación (banda 6). 

Así, el pigmento más polar es el que presenta un **menor valor de Rf** y el más apolar el que presenta un **mayor valor de Rf**.

En el extracto que hemos preparado los pigmentos que se distinguen son: **β-Caroteno, Clorofila a, Clorofila b, Luteina, Violaxantina y Neoxantina**.

**Orden de polaridad (de más apolar a más polar):**
β-Caroteno > Clorofila a > Clorofila b > Luteina > Violaxantina > Neoxantina
"""
        
        # 3. ANABAENA (D27:D28 en R, equivale a skiprows=26, nrows=2)
        try:
            abs_anabaena = pd.read_excel(file_path, sheet_name="Practica 3", usecols="D", skiprows=26, nrows=1, header=None).iloc[0, 0]
            pig_anabaena = pd.read_excel(file_path, sheet_name="Practica 3", usecols="D", skiprows=27, nrows=1, header=None).iloc[0, 0]
            print(f"  → Anabaena leída: ABS={abs_anabaena}, Pig={pig_anabaena}")
            
            df_anabaena = pd.DataFrame({
                'Resultado': ['Máximos absorción', 'Pigmento estudiante', 'Pigmento correcto'],
                'Valores': [str(abs_anabaena), pig_anabaena, 'Ficocianina']
            })
            
            results['anabaena'] = df_anabaena
            print(f"  ✓ Anabaena: {len(df_anabaena)} filas")
        except Exception as e:
            error_msg = f"Error en Anabaena: {str(e)}"
            print(f"  ✗ {error_msg}")
            results['anabaena'] = pd.DataFrame()
            results['anabaena_error'] = error_msg
        
        results['anabaena_expl'] = """
**Pigmentos en *Anabaena*:**

En el caso de la extracción de los pigmentos de *Anabaena*, no hemos usado una extracción basada en disolventes apolares. Hemos usado una pequeña cantidad de tolueno para debilitar la membrana de la bacteria para quedarnos con los elementos solubles en agua, y por lo tanto polares.

Al determinar los máximos de Absorbancia apreciamos que el pico está en la región del rojo (~620 nm), de ahí el color azulado que presenta el extracto, y que coincide con el espectro típico de la **ficocianina**.

**Preguntas:**
- ¿Has comparado el espectro de absorción *in vivo* del cultivo de *Anabaena* con el del extracto de ficocianina?
- ¿Qué pigmento enmascara el pico de absorción de ficocianina en el cultivo vivo?
"""
        
    except Exception as e:
        results['error'] = f"Error procesando Práctica 3: {e}"
    
    return results

# ============================================================================
# PRÁCTICA 4: REACCIÓN DE HILL
# ============================================================================

def process_practica4(file_path):
    """Procesa Práctica 4: Reacción de Hill y fotosíntesis"""
    results = {}
    
    # Inicializar variables por defecto para evitar NameError en bloques posteriores
    chl_corr_mg = 1.0  # Valor por defecto si falla la lectura
    df_ferri = pd.DataFrame()  # DataFrame vacío por defecto
    
    # 1. CLOROFILA EN REACCIÓN
    try:
        abs_chl = pd.read_excel(file_path, sheet_name="Practica 4", usecols="D", skiprows=5, nrows=1, header=None).iloc[0, 0]
        chl_student_ml = pd.read_excel(file_path, sheet_name="Practica 4", usecols="D", skiprows=6, nrows=1, header=None).iloc[0, 0]
        chl_student_mg = pd.read_excel(file_path, sheet_name="Practica 4", usecols="D", skiprows=7, nrows=1, header=None).iloc[0, 0]
        
        chl_corr_ml = round(abs_chl / 76.07 * 100, 2)
        chl_corr_mg = round(chl_corr_ml * 0.5, 2)
        
        df_chl_hill = pd.DataFrame({
            'Parámetro': ['ABS', 'Chla tilacoides mg/mL', 'mg Chla en reacción'],
            'Estudiante': [abs_chl, chl_student_ml, chl_student_mg],
            'Correcto': [abs_chl, chl_corr_ml, chl_corr_mg]
        })
        df_chl_hill['Validación'] = validate_column(df_chl_hill, 'Estudiante', 'Correcto')
        
        results['chl_hill'] = df_chl_hill
        results['chl_hill_expl'] = rf"""
**Determinación de la concentración de Chl a en reacción de Hill:**

En la práctica 4 hemos determinado la concentración de clorofila en el extracto de tilacoides diluido 100 veces, por lo que para calcular la concentración en el extracto:

$$[\text{{Chla tilacoides}}] (\text{{mg/mL}}) = \frac{{\text{{ABS}}_{{665}}}}{{76.07 \cdot 1 \text{{ cm}}}} \times 100 \frac{{\text{{mg}}}}{{\text{{mL}}}}$$

Por otro lado, para calcular la cantidad en mg de Chla en la reacción de Hill hemos de tener en cuenta que hemos añadido 0.5 mL del extracto de tilacoides a la reacción. Por ello:

$$\text{{mg Chla en reacción}} = [\text{{Chla tilacoides}}] \frac{{\text{{mg Chla}}}}{{\text{{mL Extracto}}}} \times 0.5 \text{{ mL Extracto}}$$

**Valor calculado:** {chl_corr_mg} mg Chla
"""
        print(f"  ✓ Clorofila Hill: {len(df_chl_hill)} filas")
    except Exception as e:
        print(f"  ✗ Error en Clorofila Hill: {e}")
        results['chl_hill'] = pd.DataFrame()
        results['chl_hill_expl'] = "Error al procesar datos de clorofila"
    
    # 2. FERRICIANURO
    try:
        df_ferri = pd.read_excel(file_path, sheet_name="Practica 4", usecols="B:D", skiprows=11, nrows=9)
        df_ferri.columns = ['Tubo', 'Abs 420 nm', '[Ferricianuro] estudiante']
        df_ferri['[Ferricianuro] correcto'] = round(df_ferri['Abs 420 nm'] * 4, 2)
        df_ferri['Validación'] = validate_column(df_ferri, '[Ferricianuro] estudiante', '[Ferricianuro] correcto')
        
        results['ferricianuro'] = df_ferri
        results['ferri_expl'] = r"""
**Concentración de Ferricianuro:**

En la práctica 4 hemos determinado la concentración de ferricianuro en la reacción de Hill. Para ello hemos medido la absorbancia a 420 nm de una mezcla diluida.

Hemos de tener en cuenta que el coeficiente de extinción del ferricianuro (ε) a 420 nm es 1 mL·µmol⁻¹·cm⁻¹. Por lo tanto la concentración de ferricianuro en la disolución que hemos medido será:

$$[\text{Ferricianuro}]_{\text{determinado}} = \frac{\text{ABS}}{1 \text{ mL} \cdot \mu\text{mol}^{-1} \cdot \text{cm}^{-1}}$$

Sin embargo para obtener el valor en la mezcla de reacción, hemos de tener en cuenta que hemos diluido la reacción 4 veces, por lo que hemos de multiplicar el valor de absorbancia por 4 para obtener la absorbancia de la reacción sin diluir.

$$[\text{Ferricianuro}]_{\text{reacción}} = [\text{Ferricianuro}]_{\text{determinado}} \times 4$$
"""
        
        # Versión PDF (sin ecuaciones LaTeX, solo Unicode)
        results['ferri_expl_pdf'] = """
**Concentración de Ferricianuro:**

En la práctica 4 hemos determinado la concentración de ferricianuro en la reacción de Hill. Para ello hemos medido la absorbancia a 420 nm de una mezcla diluida.

Hemos de tener en cuenta que el coeficiente de extinción del ferricianuro (ε) a 420 nm es 1 mL·µmol⁻¹·cm⁻¹. Por lo tanto la concentración de ferricianuro en la disolución que hemos medido será:

[Ferricianuro] = ABS / (1 mL·µmol⁻¹·cm⁻¹)

Sin embargo para obtener el valor en la mezcla de reacción, hemos de tener en cuenta que hemos diluido la reacción 4 veces, por lo que hemos de multiplicar el valor de absorbancia por 4 para obtener la absorbancia de la reacción sin diluir.

[Ferricianuro]reacción = [Ferricianuro]determinado × 4
"""
        print(f"  ✓ Ferricianuro: {len(df_ferri)} filas")
    except Exception as e:
        print(f"  ✗ Error en Ferricianuro: {e}")
        results['ferricianuro'] = pd.DataFrame()
        results['ferri_expl'] = "Error al procesar datos de ferricianuro"
        
    # 3. ACTIVIDAD FOTOSINTÉTICA (B24:D27 sin cabecera, skiprows=23, nrows=4)
    try:
        df_hill = pd.read_excel(file_path, sheet_name="Practica 4", usecols="B:D", skiprows=23, nrows=4, header=None)
        print(f"  → Hill leído: {df_hill.shape}")
        df_hill.columns = ['Tubo', 'Tiempo (min)', 'Reducción estudiante']
        
        # Verificar que df_ferri tiene suficientes filas antes de usarlo
        if len(df_ferri) >= 7:
            # df_hill tiene 4 filas (tubos 4-7), necesitamos índices 3:7 de df_ferri (4 valores)
            df_hill['Reducción corregido'] = np.round(df_ferri['[Ferricianuro] correcto'].iloc[3:7].values * 3.5 / chl_corr_mg, 2)
        else:
            print(f"  ⚠ Ferricianuro insuficiente ({len(df_ferri)} filas), usando valores por defecto")
            df_hill['Reducción corregido'] = 0.0
        
        # Regresión lineal Hill
        x_hill = df_hill['Tiempo (min)'].values
        y_hill = df_hill['Reducción corregido'].values
        slope_hill, intercept_hill, _, _, _ = linregress(x_hill, y_hill)
        
        fig_hill, ax = plt.subplots(figsize=(10, 7))
        ax.scatter(x_hill, y_hill, s=100, alpha=0.7, color='#27ae60', edgecolors='black', linewidths=2, label='Datos', zorder=3)
        ax.plot(x_hill, slope_hill * x_hill + intercept_hill, 'b-', linewidth=3, label='Regresión lineal', zorder=2)
        ax.set_xlabel('Tiempo reacción (min)', fontsize=14, fontweight='bold')
        ax.set_ylabel('µmol Fe³⁺CN · mg Chl⁻¹', fontsize=14, fontweight='bold')
        ax.set_title('Reacción de Hill - Reducción de Ferricianuro', fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=12, frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.draw()  # Dibujar la figura
        
        # Calcular actividades
        vel_min = abs(round(slope_hill, 2))
        vel_hora = round(vel_min * 60, 2)
        vel_o2 = round(vel_hora / 4, 2)
        
        # Calcular actividad DCMU solo si df_ferri tiene suficientes datos
        if len(df_ferri) >= 8:
            dcmu_activity = round((df_ferri['[Ferricianuro] correcto'].iloc[3] - df_ferri['[Ferricianuro] correcto'].iloc[7]) * 3.5 * 4 / chl_corr_mg, 2)
        else:
            dcmu_activity = 0.0
        
        df_foto = pd.DataFrame({
            'Parámetro': [
                'Velocidad Hill (µmol Fe³⁺CN · mg Chl⁻¹ · min⁻¹)', 
                'Actividad FSII (µmol Fe³⁺CN · mg Chl⁻¹ · h⁻¹)', 
                'Liberación O₂ (µmol O₂ · mg Chl⁻¹ · h⁻¹)', 
                'Actividad FSII+DCMU (µmol Fe³⁺CN · mg Chl⁻¹ · min⁻¹)'
            ],
            'Valor': [vel_min, vel_hora, vel_o2, dcmu_activity]
        })
        
        results['hill'] = df_hill
        results['hill_fig'] = fig_hill
        results['fotosintesis'] = df_foto
        
        # Generar explicación con los valores calculados (versión DASHBOARD con LaTeX)
        results['foto_expl'] = rf"""
**Actividad Fotosintética - Reacción de Hill:**

Para obtener los valores de µmoles de Ferricianuro por miligramo de clorofila en cada tiempo de reacción (tubos 4 a 7), hemos de multiplicar la concentración por el volumen de la muestra, 3.5 mL, y dividirlo por la cantidad de clorofila que hemos añadido con nuestra suspensión de tilacoides que en este caso es **{chl_corr_mg} mg Chla**.

Podemos representar los valores obtenidos frente al tiempo (0, 5, 10, 15 minutos) en un gráfico y calcular la pendiente. Dicha pendiente, de signo negativo dado que estamos observando una disminución de la concentración de Fe³⁺CN, nos da la velocidad de reacción de la enzima.

En este caso, la pendiente es de **{vel_min}** µmol Fe³⁺CN·mg Chl⁻¹·min⁻¹.

Si multiplicamos esta pendiente por 60, obtendremos la velocidad de reacción en una hora: **{vel_hora}** µmol Fe³⁺CN·mg Chl⁻¹·h⁻¹.

Sabemos que:

$$\text{{Fe}}^{{3+}}\text{{CN}} + 1e^- \Rightarrow \text{{Fe}}^{{2+}}\text{{CN}}$$

También sabemos que en la reacción de fotólisis del agua:

$$2\text{{H}}_2\text{{O}} + h\nu \Rightarrow \text{{O}}_2 + 4\text{{H}}^+ + 4e^-$$

Por lo tanto por cada µmol de O₂ se liberan 4 µmoles de e⁻. Si dividimos esta velocidad por 4, obtendremos la actividad del FSII en forma de liberación de O₂:

**{vel_o2}** µmol O₂·mg Chl⁻¹·h⁻¹

Finalmente, si añadimos **DCMU**, que captura los electrones al nivel de la plastoquinona compitiendo por el FeCN, se aprecia un descenso en la tasa de reducción del FeCN. Para calcular esa tasa hemos comparado el valor del tubo 4 (tiempo 0) con el del tubo con el DCMU a los 15 minutos de reacción (tubo 8) con la siguiente fórmula:

$$\text{{Reducción Fe}}^{{3+}}\text{{CN}} = -\frac{{[\text{{Fe}}^{{3+}}\text{{CN}}]_{{\text{{Tubo 8}}}} - [\text{{Fe}}^{{3+}}\text{{CN}}]_{{\text{{Tubo 4}}}}}}{{15 \text{{ min}} - 0 \text{{ min}}}} \times \frac{{60 \text{{ min}}}}{{1 \text{{ h}}}}$$

**Actividad FSII + DCMU:** {dcmu_activity} µmol Fe²⁺CN·mg Chl⁻¹·h⁻¹
"""
        
        # Versión PDF (sin ecuaciones LaTeX, solo Unicode)
        results['foto_expl_pdf'] = f"""
**Actividad Fotosintética - Reacción de Hill:**

Para obtener los valores de µmoles de Ferricianuro por miligramo de clorofila en cada tiempo de reacción (tubos 4 a 7), hemos de multiplicar la concentración por el volumen de la muestra, 3.5 mL, y dividirlo por la cantidad de clorofila que hemos añadido con nuestra suspensión de tilacoides que en este caso es **{chl_corr_mg} mg Chla**.

Podemos representar los valores obtenidos frente al tiempo (0, 5, 10, 15 minutos) en un gráfico y calcular la pendiente. Dicha pendiente, de signo negativo dado que estamos observando una disminución de la concentración de Fe³⁺CN, nos da la velocidad de reacción de la enzima.

En este caso, la pendiente es de **{vel_min}** µmol Fe³⁺CN·mg Chl⁻¹·min⁻¹.

Si multiplicamos esta pendiente por 60, obtendremos la velocidad de reacción en una hora: **{vel_hora}** µmol Fe³⁺CN·mg Chl⁻¹·h⁻¹.

Sabemos que: Fe³⁺CN + 1e⁻ → Fe²⁺CN

También sabemos que en la reacción de fotólisis del agua: 2H₂O + luz → O₂ + 4H⁺ + 4e⁻

Por lo tanto por cada µmol de O₂ se liberan 4 µmoles de e⁻. Si dividimos esta velocidad por 4, obtendremos la actividad del FSII en forma de liberación de O₂:

**{vel_o2}** µmol O₂·mg Chl⁻¹·h⁻¹

Finalmente, si añadimos **DCMU**, que captura los electrones al nivel de la plastoquinona compitiendo por el FeCN, se aprecia un descenso en la tasa de reducción del FeCN. Para calcular esa tasa hemos comparado el valor del tubo 4 (tiempo 0) con el del tubo con el DCMU a los 15 minutos de reacción (tubo 8).

**Actividad FSII + DCMU:** {dcmu_activity} µmol Fe²⁺CN·mg Chl⁻¹·h⁻¹
"""
        
        print(f"  ✓ Hill: {len(df_hill)} filas, Fotosíntesis: {len(df_foto)} filas")
    except Exception as e:
        error_msg = f"Error en Hill/Fotosíntesis: {str(e)}"
        print(f"  ✗ {error_msg}")
        results['hill'] = pd.DataFrame()
        results['hill_fig'] = None
        results['fotosintesis'] = pd.DataFrame()
        results['hill_error'] = error_msg
        # Explicación genérica si falla el procesamiento
        results['foto_expl'] = """
**Actividad Fotosintética - Reacción de Hill:**

No se pudieron calcular los parámetros de la reacción de Hill. Verifique que los datos de entrada sean correctos.
"""
    
    return results

# ============================================================================
# PRÁCTICA 5: α-AMILASA
# ============================================================================

def process_practica5(file_path):
    """Procesa Práctica 5: Germinación y α-amilasa"""
    results = {}
    
    try:
        # 1. GERMINACIÓN
        germinacion = pd.read_excel(file_path, sheet_name="Practica 5", usecols="E", skiprows=3, nrows=1, header=None).iloc[0, 0]
        results['germinacion'] = germinacion
        results['germ_expl'] = f"""
        **Germinación de semillas:** {germinacion}%
        
        ¿Este paquete de semillas es adecuado para la práctica? (Se considera adecuado >80%)
        """
        
        # 2. α-AMILASA (B10:I15 en R, equivale a skiprows=10, nrows=5 - saltando encabezado)
        try:
            df_amil = pd.read_excel(file_path, sheet_name="Practica 5", usecols="B:I", skiprows=10, nrows=5, header=None)
            print(f"  → Amilasa leída: {df_amil.shape}")
            # Estructura real: Número, Tipo semilla, Tratamiento, Peso seco, Abs t=0, Abs t=10, Almidón deg/h, Actividad
            df_amil.columns = ['Número', 'Tipo semilla', 'Tratamiento', 'Peso seco (mg)', 
                           'Abs t=0', 'Abs t=10', 'Almidón deg/h estudiante', 'Actividad estudiante']
            
            # Convertir columnas numéricas a float (por si hay strings)
            for col in ['Peso seco (mg)', 'Abs t=0', 'Abs t=10', 'Almidón deg/h estudiante', 'Actividad estudiante']:
                df_amil[col] = pd.to_numeric(df_amil[col], errors='coerce')
            
            # Calcular valores corregidos
            df_amil['Almidón deg/h correcto'] = np.round((df_amil['Abs t=0'] - df_amil['Abs t=10']) / 11.4 * 7 * 6, 2)
            mg_semillas_reaccion = df_amil['Peso seco (mg)'] / 10 * 0.25
            df_amil['Actividad corregida'] = np.round(df_amil['Almidón deg/h correcto'] / mg_semillas_reaccion, 2)
            
            df_amil['Val. Almidón'] = validate_column(df_amil, 'Almidón deg/h estudiante', 'Almidón deg/h correcto')
            df_amil['Val. Actividad'] = validate_column(df_amil, 'Actividad estudiante', 'Actividad corregida')
            
            # Gráfica
            fig_amil, ax = plt.subplots(figsize=(12, 7))
            x_pos = np.arange(len(df_amil))
            colors_amil = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
            bars = ax.bar(x_pos, df_amil['Actividad corregida'], color=colors_amil, edgecolor='black', linewidth=1.0)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(df_amil['Tratamiento'], fontsize=12, rotation=20, ha='right')
            ax.set_xlabel('Tratamiento', fontsize=14, fontweight='bold')
            ax.set_ylabel('Actividad α-amilasa (mg almidón·mg semilla⁻¹·h⁻¹)', fontsize=13, fontweight='bold')
            ax.set_title('Inducción de actividad α-amilasa en cebada', fontsize=16, fontweight='bold', pad=20)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
            plt.tight_layout()
            plt.draw()  # Dibujar la figura
            
            results['amilasa'] = df_amil
            results['amilasa_fig'] = fig_amil
            print(f"  ✓ Amilasa: {len(df_amil)} filas")
        except Exception as e:
            error_msg = f"Error en Amilasa: {str(e)}"
            print(f"  ✗ {error_msg}")
            results['amilasa'] = pd.DataFrame()
            results['amilasa_fig'] = None
            results['amilasa_error'] = error_msg
        
        results['amilasa_expl'] = r"""
**Inducción de actividad α-amilasa en cebada:**

La actividad de la α-amilasa se ha calculado a partir de la degradación del almidón. Para ello, se ha medido la absorbancia de la solución de almidón en el tiempo 0 y a los 10 minutos de reacción. La actividad de la α-amilasa se ha calculado con la siguiente fórmula:

$$\text{Almidón degradado (mg/h)} = \frac{(\text{Abs}_{t=0} - \text{Abs}_{t=10}) \cdot 1\text{cm}}{11.4 \text{ mL} \cdot \text{mg}^{-1} \cdot \text{cm}^{-1}} \times 7 \text{ mL} \times \frac{60 \text{ min}}{10 \text{ min} \cdot \text{h}}$$

Es importante tener en cuenta que no todos los experimentos parten de la misma cantidad de material biológico, ya que el peso seco de las semillas varía entre los casos. Por esta razón, es necesario **normalizar** los resultados para permitir una comparación adecuada entre ellos.

En este procedimiento, utilizaremos el peso seco de las semillas como factor de normalización, expresando la actividad de α-amilasa como la cantidad de almidón degradado (en mg) por hora, por mg de semilla.

Para llevar a cabo este cálculo, recordemos que el extracto enzimático de semillas se ha obtenido homogenizando el peso seco de las semillas de cada caso en un volumen final de 10 mL de tampón. De este homogenizado, se tomaron 0.25 mL para la reacción. Por lo tanto, debemos determinar cuántos mg de semillas están representados en esos 0.25 mL de extracto:

$$\text{mg semillas en 0.25 mL} = \frac{\text{mg semillas en placa}}{10 \text{ mL}} \times 0.25 \text{ mL}$$

Finalmente, para referir la actividad de la α-amilasa a la cantidad de semillas utilizadas, hemos de dividir la actividad de la α-amilasa por los mg de semillas utilizados. El resultado se expresa en mg de almidón degradado por hora y mg de semillas.

**Preguntas clave para el análisis:**

- ¿Qué placas hemos de comparar para determinar la influencia del embrión?
- ¿Qué placas hemos de comparar para determinar la influencia de la Giberelina? ¿Induce la actividad germinativa o no? ¿Dónde se produce la Giberelina? ¿Cuál es su diana?
- ¿Qué placas hemos de comparar para determinar si la actividad alfa amilasa depende de la regulación transcripcional? ¿Hay actividad alfa amilasa independiente del embrión o de la Giberelina?
"""
        
    except Exception as e:
        results['error'] = f"Error procesando Práctica 5: {e}"
    
    return results

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def process_all_practicas(file):
    """Procesa todas las 5 prácticas y devuelve TODOS los outputs"""
    
    if file is None:
        empty_results = [None] * 34  # 34 outputs vacíos (35 total - 1 mensaje)
        return ["⚠️ Por favor, suba un archivo Excel"] + empty_results
    
    try:
        file_path = file.name
        
        # Validar archivo
        sheets = pd.ExcelFile(file_path).sheet_names
        if "INFO PAREJA" not in sheets:
            empty_results = [None] * 34
            return ["❌ El archivo no tiene el formato correcto"] + empty_results
        
        # ========================================================================
        # PASO 1: PROCESAR TODAS LAS PRÁCTICAS
        # ========================================================================
        print("\n" + "="*60)
        print("INICIANDO PROCESAMIENTO DE PRÁCTICAS")
        print("="*60)
        
        print("\n[1/5] Procesando Práctica 1...")
        p1 = process_practica1(file_path)
        print(f"     Resultado P1: {len(p1)} elementos")
        
        print("\n[2/5] Procesando Práctica 2...")
        p2 = process_practica2(file_path)
        print(f"     Resultado P2: {len(p2)} elementos")
        
        print("\n[3/5] Procesando Práctica 3...")
        p3 = process_practica3(file_path)
        print(f"     Resultado P3: {len(p3)} elementos")
        
        print("\n[4/5] Procesando Práctica 4...")
        p4 = process_practica4(file_path)
        print(f"     Resultado P4: {len(p4)} elementos")
        
        print("\n[5/5] Procesando Práctica 5...")
        p5 = process_practica5(file_path)
        print(f"     Resultado P5: {len(p5)} elementos")
        
        print("\n[PDF] Generando informe PDF...")
        try:
            pdf_path = generate_simple_pdf({'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5})
            if pdf_path is None:
                print("     ✗ Error: No se pudo generar el PDF")
                pdf_path = None  # Asegurar que es None
            else:
                print(f"     ✓ PDF generado en: {pdf_path}")
        except Exception as e:
            print(f"     ✗ Error generando PDF: {e}")
            import traceback
            traceback.print_exc()
            pdf_path = None
        
        # ========================================================================
        # PASO 2: EXTRAER TODOS LOS RESULTADOS EN ORDEN
        # ========================================================================
        
        # STATUS CON INFORMACIÓN DETALLADA
        # Recopilar errores para mostrar
        errors_list = []
        if p2.get('corn_error'): errors_list.append(f"• P2-Maíz: {p2['corn_error']}")
        if p2.get('pea_error'): errors_list.append(f"• P2-Guisante: {p2['pea_error']}")
        if p3.get('croma_error'): errors_list.append(f"• P3-Cromatografía: {p3['croma_error']}")
        if p3.get('anabaena_error'): errors_list.append(f"• P3-Anabaena: {p3['anabaena_error']}")
        if p4.get('hill_error'): errors_list.append(f"• P4-Hill: {p4['hill_error']}")
        if p5.get('amilasa_error'): errors_list.append(f"• P5-Amilasa: {p5['amilasa_error']}")
        
        errors_html = ""
        if errors_list:
            errors_html = f"""
            <div style='background: #fff3cd; border: 2px solid #ffc107; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                <h4 style='color: #856404; margin-top: 0;'>⚠️ Errores Detectados:</h4>
                <ul style='color: #856404; margin: 5px 0; font-size: 11px;'>
                    {''.join([f'<li>{err}</li>' for err in errors_list])}
                </ul>
            </div>
            """
        
        debug_info = f"""
        <div style='background: #e8f4f8; border: 2px solid #17a2b8; border-radius: 10px; padding: 15px; margin: 10px 0; font-family: monospace; font-size: 12px;'>
            <h4 style='color: #0c5460; margin-top: 0;'>📊 Información de Procesamiento:</h4>
            <ul style='color: #0c5460; margin: 5px 0;'>
                <li>✓ P1 - Sacarosa: {len(p1.get('sacarosa', pd.DataFrame()))} filas</li>
                <li>✓ P1 - Cebolla: {len(p1.get('onion', pd.DataFrame()))} filas, Figura: {'OK' if p1.get('onion_fig') is not None else 'FALTA'}</li>
                <li>✓ P1 - Patata: {len(p1.get('potato', pd.DataFrame()))} filas, Figura: {'OK' if p1.get('potato_fig') is not None else 'FALTA'}</li>
                <li>✓ P2 - Maíz: {len(p2.get('corn', pd.DataFrame()))} filas, Figura: {'OK' if p2.get('corn_fig') is not None else 'FALTA'}</li>
                <li>✓ P2 - Guisante: {len(p2.get('pea', pd.DataFrame()))} filas, Figuras: {'OK' if p2.get('pea_fig1') and p2.get('pea_fig2') else 'FALTA'}</li>
                <li>✓ P3 - Clorofila: {len(p3.get('clorofila', pd.DataFrame()))} filas</li>
                <li>✓ P3 - Cromatografía: {len(p3.get('cromatografia', pd.DataFrame()))} filas</li>
                <li>✓ P3 - Anabaena: {len(p3.get('anabaena', pd.DataFrame()))} filas</li>
                <li>✓ P4 - Chl Hill: {len(p4.get('chl_hill', pd.DataFrame()))} filas</li>
                <li>✓ P4 - Ferricianuro: {len(p4.get('ferricianuro', pd.DataFrame()))} filas</li>
                <li>✓ P4 - Hill: {len(p4.get('hill', pd.DataFrame()))} filas, Figura: {'OK' if p4.get('hill_fig') is not None else 'FALTA'}</li>
                <li>✓ P4 - Fotosíntesis: {len(p4.get('fotosintesis', pd.DataFrame()))} filas</li>
                <li>✓ P5 - Germinación: {p5.get('germinacion', 'N/A')}%</li>
                <li>✓ P5 - Amilasa: {len(p5.get('amilasa', pd.DataFrame()))} filas, Figura: {'OK' if p5.get('amilasa_fig') is not None else 'FALTA'}</li>
                <li>✓ PDF: {'Generado' if pdf_path else 'ERROR'}</li>
            </ul>
        </div>
        {errors_html}
        """
        
        output_01_status = f"""
        <div style='background: #d4edda; border: 2px solid #28a745; border-radius: 10px; padding: 20px; margin: 10px 0;'>
            <h2 style='color: #155724; margin-top: 0;'>✅ ANÁLISIS COMPLETADO CON ÉXITO</h2>
            <p style='font-size: 16px; color: #155724;'>
                Las 5 prácticas han sido procesadas correctamente.<br>
                Revise los resultados detallados a continuación.
            </p>
        </div>
        {debug_info}
        """
        
        # PRÁCTICA 1 - SACAROSA (2 outputs)
        output_02_df_sac = p1.get('sacarosa', pd.DataFrame())
        if output_02_df_sac.empty:
            output_02_df_sac = pd.DataFrame({'ERROR': ['No se pudo leer la hoja Practica 1']})
        output_03_sac_expl = p1.get('sacarosa_expl', '')
        
        # PRÁCTICA 1 - CEBOLLA (3 outputs)
        output_04_df_onion = p1.get('onion', pd.DataFrame())
        if output_04_df_onion.empty:
            output_04_df_onion = pd.DataFrame({'ERROR': ['No se pudieron leer datos de cebolla']})
        output_05_fig_onion = p1.get('onion_fig', None)
        output_06_onion_expl = p1.get('onion_expl', '')
        
        # PRÁCTICA 1 - PATATA (3 outputs)
        output_07_df_potato = p1.get('potato', pd.DataFrame())
        if output_07_df_potato.empty:
            output_07_df_potato = pd.DataFrame({'ERROR': ['No se pudieron leer datos de patata']})
        output_08_fig_potato = p1.get('potato_fig', None)
        output_09_potato_expl = p1.get('potato_expl', '')
        
        # PRÁCTICA 2 - MAÍZ (3 outputs)
        output_10_df_corn = p2.get('corn', pd.DataFrame())
        if output_10_df_corn.empty:
            output_10_df_corn = pd.DataFrame({'ERROR': ['No se pudieron leer datos de maíz']})
        output_11_fig_corn = p2.get('corn_fig', None)
        output_12_corn_expl = p2.get('corn_expl', '')
        
        # PRÁCTICA 2 - GUISANTE (4 outputs)
        output_13_df_pea = p2.get('pea', pd.DataFrame())
        if output_13_df_pea.empty:
            output_13_df_pea = pd.DataFrame({'ERROR': ['No se pudieron leer datos de guisante']})
        output_14_fig_pea1 = p2.get('pea_fig1', None)
        output_15_fig_pea2 = p2.get('pea_fig2', None)
        output_16_pea_expl = p2.get('pea_expl', '')
        
        # PRÁCTICA 3 - CLOROFILA (2 outputs)
        output_17_df_clor = p3.get('clorofila', pd.DataFrame())
        if output_17_df_clor.empty:
            output_17_df_clor = pd.DataFrame({'ERROR': ['No se pudieron leer datos de clorofila']})
        output_18_clor_expl = p3.get('clor_expl', '')
        
        # PRÁCTICA 3 - CROMATOGRAFÍA (2 outputs)
        output_19_df_croma = p3.get('cromatografia', pd.DataFrame())
        if output_19_df_croma.empty:
            output_19_df_croma = pd.DataFrame({'ERROR': ['No se pudieron leer datos de cromatografía']})
        output_20_croma_expl = p3.get('croma_expl', '')
        
        # PRÁCTICA 3 - ANABAENA (2 outputs)
        output_21_df_anabaena = p3.get('anabaena', pd.DataFrame())
        if output_21_df_anabaena.empty:
            output_21_df_anabaena = pd.DataFrame({'ERROR': ['No se pudieron leer datos de anabaena']})
        output_22_anabaena_expl = p3.get('anabaena_expl', '')
        
        # PRÁCTICA 4 - CLOROFILA HILL (2 outputs)
        output_23_df_chl_hill = p4.get('chl_hill', pd.DataFrame())
        if output_23_df_chl_hill.empty:
            output_23_df_chl_hill = pd.DataFrame({'ERROR': ['No se pudieron leer datos de clorofila Hill']})
        output_24_chl_hill_expl = p4.get('chl_hill_expl', '')
        
        # PRÁCTICA 4 - FERRICIANURO (2 outputs)
        output_25_df_ferri = p4.get('ferricianuro', pd.DataFrame())
        if output_25_df_ferri.empty:
            output_25_df_ferri = pd.DataFrame({'ERROR': ['No se pudieron leer datos de ferricianuro']})
        output_26_ferri_expl = p4.get('ferri_expl', '')
        
        # PRÁCTICA 4 - ACTIVIDAD FOTOSINTÉTICA (4 outputs)
        output_27_df_hill = p4.get('hill', pd.DataFrame())
        if output_27_df_hill.empty:
            output_27_df_hill = pd.DataFrame({'ERROR': ['No se pudieron leer datos de Hill']})
        output_28_fig_hill = p4.get('hill_fig', None)
        output_29_df_foto = p4.get('fotosintesis', pd.DataFrame())
        if output_29_df_foto.empty:
            output_29_df_foto = pd.DataFrame({'ERROR': ['No se pudieron calcular actividades']})
        output_30_foto_expl = p4.get('foto_expl', '')
        
        # PRÁCTICA 5 - GERMINACIÓN (1 output)
        output_31_germ_text = p5.get('germ_expl', '')
        
        # PRÁCTICA 5 - AMILASA (3 outputs)
        output_32_df_amil = p5.get('amilasa', pd.DataFrame())
        if output_32_df_amil.empty:
            output_32_df_amil = pd.DataFrame({'ERROR': ['No se pudieron leer datos de amilasa']})
        output_33_fig_amil = p5.get('amilasa_fig', None)
        output_34_amil_expl = p5.get('amilasa_expl', '')
        
        # PDF (1 output)
        output_35_pdf = pdf_path
        
        # ========================================================================
        # PASO 3: VALIDAR DATOS ANTES DE RETORNAR
        # ========================================================================
        print("\n" + "="*60)
        print("VALIDACIÓN DE OUTPUTS")
        print("="*60)
        print(f"Output 02 (df_sac): {type(output_02_df_sac).__name__} - {len(output_02_df_sac) if hasattr(output_02_df_sac, '__len__') else 'N/A'} filas")
        print(f"Output 04 (df_onion): {type(output_04_df_onion).__name__} - {len(output_04_df_onion) if hasattr(output_04_df_onion, '__len__') else 'N/A'} filas")
        print(f"Output 05 (fig_onion): {'OK' if output_05_fig_onion is not None else 'NONE'}")
        print(f"Output 10 (df_corn): {type(output_10_df_corn).__name__} - {len(output_10_df_corn) if hasattr(output_10_df_corn, '__len__') else 'N/A'} filas")
        print(f"Output 11 (fig_corn): {'OK' if output_11_fig_corn is not None else 'NONE'}")
        print(f"Output 19 (df_croma): {type(output_19_df_croma).__name__} - {len(output_19_df_croma) if hasattr(output_19_df_croma, '__len__') else 'N/A'} filas")
        print(f"Output 27 (df_hill): {type(output_27_df_hill).__name__} - {len(output_27_df_hill) if hasattr(output_27_df_hill, '__len__') else 'N/A'} filas")
        print(f"Output 28 (fig_hill): {'OK' if output_28_fig_hill is not None else 'NONE'}")
        print(f"Output 32 (df_amil): {type(output_32_df_amil).__name__} - {len(output_32_df_amil) if hasattr(output_32_df_amil, '__len__') else 'N/A'} filas")
        print(f"Output 33 (fig_amil): {'OK' if output_33_fig_amil is not None else 'NONE'}")
        print(f"Output 35 (PDF): {output_35_pdf}")
        
        print("\n" + "="*60)
        print("RETORNANDO 35 OUTPUTS")
        print("="*60 + "\n")
        
        return [
            output_01_status,           # 1
            output_02_df_sac,           # 2
            output_03_sac_expl,         # 3
            output_04_df_onion,         # 4
            output_05_fig_onion,        # 5
            output_06_onion_expl,       # 6
            output_07_df_potato,        # 7
            output_08_fig_potato,       # 8
            output_09_potato_expl,      # 9
            output_10_df_corn,          # 10
            output_11_fig_corn,         # 11
            output_12_corn_expl,        # 12
            output_13_df_pea,           # 13
            output_14_fig_pea1,         # 14
            output_15_fig_pea2,         # 15
            output_16_pea_expl,         # 16
            output_17_df_clor,          # 17
            output_18_clor_expl,        # 18
            output_19_df_croma,         # 19
            output_20_croma_expl,       # 20
            output_21_df_anabaena,      # 21
            output_22_anabaena_expl,    # 22
            output_23_df_chl_hill,      # 23
            output_24_chl_hill_expl,    # 24
            output_25_df_ferri,         # 25
            output_26_ferri_expl,       # 26
            output_27_df_hill,          # 27
            output_28_fig_hill,         # 28
            output_29_df_foto,          # 29
            output_30_foto_expl,        # 30
            output_31_germ_text,        # 31
            output_32_df_amil,          # 32
            output_33_fig_amil,         # 33
            output_34_amil_expl,        # 34
            output_35_pdf               # 35
        ]
        
    except Exception as e:
        import traceback
        error_msg = f"""
        <div style='background: #f8d7da; border: 2px solid #dc3545; border-radius: 10px; padding: 20px;'>
            <h2 style='color: #721c24;'>❌ ERROR AL PROCESAR</h2>
            <p style='color: #721c24;'>{str(e)}</p>
            <pre style='color: #721c24; font-size: 12px;'>{traceback.format_exc()}</pre>
        </div>
        """
        empty_results = [None] * 34
        return [error_msg] + empty_results

def generate_simple_pdf(results):
    """Genera PDF completo con todas las tablas, figuras y resultados"""
    try:
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = pdf_file.name
        pdf_file.close()  # Cerrar el archivo para que ReportLab pueda escribir
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1f4788'),
                                     spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold')
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2c3e50'),
                                       spaceAfter=8, spaceBefore=8, fontName='Helvetica-Bold')
        small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, spaceAfter=4)
        
        story = []
        story.append(Paragraph("INFORME DE PRÁCTICAS - FISIOLOGÍA VEGETAL", title_style))
        story.append(Paragraph("Universidad Autónoma de Madrid (UAM)", small_style))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", small_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Lista para mantener buffers abiertos hasta que se construya el PDF
        image_buffers = []
        
        # Helper para agregar figuras (limitar altura máxima)
        def add_figure(fig, width=14*cm, max_height=9*cm):
            if fig is not None:
                try:
                    img_buffer = io.BytesIO()
                    fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
                    img_buffer.seek(0)
                    # NO cerrar el buffer - ReportLab lo necesita abierto
                    image_buffers.append(img_buffer)  # Guardar referencia
                    img = Image(img_buffer, width=width, height=max_height, kind='proportional')
                    img.hAlign = 'CENTER'
                    story.append(img)
                    story.append(Spacer(1, 0.3*cm))
                except Exception as e:
                    print(f"  ⚠ Error añadiendo figura: {e}")
                    story.append(Paragraph(f"[Figura no disponible: {str(e)}]", small_style))
        
        # Helper para renderizar ecuaciones LaTeX como imágenes
        def latex_to_image(latex_code):
            """Convierte una ecuación LaTeX a imagen PNG para insertar en PDF"""
            try:
                import matplotlib.pyplot as plt
                import io
                
                # Crear figura más grande para la ecuación
                fig, ax = plt.subplots(figsize=(10, 1.2))
                ax.axis('off')
                
                # Renderizar LaTeX con fuente más grande
                ax.text(0.5, 0.5, f'${latex_code}$', 
                       fontsize=16, ha='center', va='center',
                       transform=ax.transAxes)
                
                # Guardar como imagen
                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight', 
                           pad_inches=0.1, dpi=200, transparent=False,
                           facecolor='white')
                plt.close(fig)
                buf.seek(0)
                
                # Añadir a lista de buffers
                image_buffers.append(buf)
                
                # Crear objeto Image de ReportLab más grande
                img = Image(buf, width=14*cm, height=1.5*cm, kind='proportional')
                return img
            except Exception as e:
                print(f"  ⚠ Error renderizando LaTeX: {e}")
                return None
        
        # Helper para agregar texto simple (sin procesamiento LaTeX)
        def add_text_simple(text):
            """Añade texto al PDF sin procesar LaTeX, para textos que ya tienen Unicode correcto"""
            if text:
                try:
                    import re
                    text = str(text)
                    
                    # Solo convertir markdown **texto** a negrita
                    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
                    
                    # Limpiar espacios múltiples y saltos de línea
                    text = re.sub(r'\n+', '\n', text)
                    text = re.sub(r' +', ' ', text)
                    text = text.strip()
                    
                    if len(text) > 1500:
                        text = text[:1500] + '...'
                    
                    # Escapar XML (excepto tags <b>)
                    if '&amp;' not in text:
                        text = text.replace('&', '&amp;')
                    text = re.sub(r'<(?!/?(b|i|u)>)', '&lt;', text)
                    text = re.sub(r'(?<!</(b|i|u))>(?!)', '&gt;', text)
                    
                    if text:
                        paragraphs = text.split('\n')
                        for para in paragraphs:
                            para = para.strip()
                            if para:
                                story.append(Paragraph(para, small_style))
                        story.append(Spacer(1, 0.2*cm))
                except Exception as e:
                    print(f"  ⚠ Error añadiendo texto: {e}")
        
        # Helper para agregar texto explicativo con conversión LaTeX mejorada
        def add_text(text):
            if text:
                try:
                    import re
                    text = str(text)

                    
                    # Eliminar etiquetas HTML
                    text = re.sub(r'<span[^>]*>', '', text)
                    text = re.sub(r'</span>', '', text)
                    text = re.sub(r'<[^>]+>', '', text)
                    
                    # Extraer y procesar ecuaciones $$...$$
                    parts = []
                    last_end = 0
                    
                    for match in re.finditer(r'\$\$([^$]+)\$\$', text):
                        # Añadir texto antes de la ecuación
                        if match.start() > last_end:
                            text_before = text[last_end:match.start()].strip()
                            if text_before:
                                parts.append(('text', text_before))
                        
                        # Añadir la ecuación como imagen
                        latex_eq = match.group(1).strip()
                        parts.append(('equation', latex_eq))
                        last_end = match.end()
                    
                    # Añadir texto restante
                    if last_end < len(text):
                        text_after = text[last_end:].strip()
                        if text_after:
                            parts.append(('text', text_after))
                    
                    # Si no hay ecuaciones, procesar como antes
                    if not parts:
                        parts = [('text', text)]
                    
                    # Procesar cada parte
                    for part_type, content in parts:
                        if part_type == 'equation':
                            # Renderizar ecuación como imagen
                            eq_img = latex_to_image(content)
                            if eq_img:
                                story.append(eq_img)
                                story.append(Spacer(1, 0.1*cm))
                        else:
                            # Procesar texto normal (puede venir con Unicode o LaTeX)
                            # 1. Convertir markdown **texto** a negrita
                            content = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', content)
                            
                            # 2. Solo convertir símbolos LaTeX si existen (el texto puede venir ya con Unicode)
                            if '\\' in content:
                                latex_map = {
                                    '\\mu': 'μ', '\\alpha': 'α', '\\beta': 'β', 
                                    '\\gamma': 'γ', '\\delta': 'δ', '\\sigma': 'σ',
                                    '\\Psi': 'Ψ', '\\Delta': 'Δ', '\\pi': 'π',
                                    '\\cdot': '·', '\\times': '×',
                                }
                                
                                for latex, unicode_char in latex_map.items():
                                    content = content.replace(latex, unicode_char)
                                
                                # Limpiar comandos LaTeX \text{...}
                                content = re.sub(r'\\text\{([^}]*)\}', r'\1', content)
                                content = re.sub(r'\\color\{[^}]+\}\{([^}]*)\}', r'\1', content)
                                
                                # Limpiar comandos LaTeX restantes
                                content = re.sub(r'\\[a-zA-Z]+', '', content)
                                content = content.replace('\\', '')
                            
                            # 3. Solo procesar super/subíndices LaTeX si hay ^ o _ seguidos de llaves
                            if '^{' in content or '_{' in content:
                                # Superíndices con llaves: ^{...}
                                def convert_superscript(match):
                                    text = match.group(1)
                                    result = ''
                                    for char in text:
                                        if char == '-':
                                            result += '⁻'
                                        elif char == '+':
                                            result += '⁺'
                                        elif char.isdigit():
                                            digit_map = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}
                                            result += digit_map.get(char, char)
                                        else:
                                            result += char
                                    return result
                                
                                content = re.sub(r'\^{([^}]+)}', convert_superscript, content)
                                
                                # Subíndices con llaves: _{...}
                                def convert_subscript(match):
                                    text = match.group(1)
                                    result = ''
                                    for char in text:
                                        if char.isdigit():
                                            sub_map = {'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉'}
                                            result += sub_map.get(char, char)
                                        elif char.isalpha():
                                            sub_alpha = {'s':'ₛ','w':'ᵥᵥ','p':'ₚ','h':'ₕ','a':'ₐ','e':'ₑ','i':'ᵢ','o':'ₒ','u':'ᵤ'}
                                            result += sub_alpha.get(char, char)
                                        else:
                                            result += char
                                    return result
                                
                                content = re.sub(r'_{([^}]+)}', convert_subscript, content)
                                
                                # Limpiar llaves restantes
                                content = content.replace('{', '').replace('}', '')
                            
                            # 4. Procesar super/subíndices simples sin llaves solo si existen
                            if '^' in content or '_' in content:
                                # Superíndices simples
                                content = content.replace('^-1', '⁻¹').replace('^-2', '⁻²').replace('^-3', '⁻³')
                                content = content.replace('^1', '¹').replace('^2', '²').replace('^3', '³').replace('^4', '⁴')
                                # Subíndices simples
                                content = content.replace('_s', 'ₛ').replace('_w', 'ᵥᵥ').replace('_p', 'ₚ').replace('_h', 'ₕ')
                                content = content.replace('_2', '₂').replace('_0', '₀')

                            
                            # Limpiar espacios
                            content = re.sub(r'\n+', '\n', content)
                            content = re.sub(r' +', ' ', content)
                            content = content.strip()
                            
                            if len(content) > 1500:
                                content = content[:1500] + '...'
                            
                            # Escapar XML (excepto tags <b>)
                            if '&amp;' not in content:
                                content = content.replace('&', '&amp;')
                            # No escapar < y > que son parte de <b> y </b>
                            content = re.sub(r'<(?!/?(b|i|u)>)', '&lt;', content)
                            content = re.sub(r'(?<!</(b|i|u))>(?!)', '&gt;', content)
                            
                            if content:
                                paragraphs = content.split('\n')
                                for para in paragraphs:
                                    para = para.strip()
                                    if para:
                                        story.append(Paragraph(para, small_style))
                                story.append(Spacer(1, 0.2*cm))
                                
                except Exception as e:
                    print(f"  ⚠ Error añadiendo texto: {e}")
        
        # Helper para limpiar texto LaTeX en celdas de tabla
        def clean_latex(text):
            """Limpia símbolos LaTeX en texto de tablas"""
            if not isinstance(text, str):
                return text
            
            import re
            
            # Convertir símbolos LaTeX PRIMERO
            latex_map = {
                '\\mu': 'μ', '\\alpha': 'α', '\\beta': 'β', 
                '\\gamma': 'γ', '\\delta': 'δ', '\\sigma': 'σ',
                '\\Psi': 'Ψ', '\\Delta': 'Δ', '\\pi': 'π',
                '\\cdot': '·', '\\times': '×',
            }
            
            for latex, unicode_char in latex_map.items():
                text = text.replace(latex, unicode_char)
            
            # Limpiar \text{...}
            text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
            
            # Convertir superíndices con llaves ANTES de limpiar llaves
            def convert_super(m):
                t = m.group(1)
                result = ''
                for c in t:
                    if c == '-': result += '⁻'
                    elif c == '+': result += '⁺'
                    elif c.isdigit():
                        result += {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}[c]
                    else: result += c
                return result
            
            text = re.sub(r'\^{([^}]+)}', convert_super, text)
            
            # Subíndices con llaves
            def convert_sub(m):
                t = m.group(1)
                result = ''
                for c in t:
                    if c.isdigit():
                        result += {'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉'}[c]
                    elif c.isalpha():
                        sub_map = {'s':'ₛ','w':'ᵥᵥ','p':'ₚ','h':'ₕ','a':'ₐ','e':'ₑ'}
                        result += sub_map.get(c, c)
                    else: result += c
                return result
            
            text = re.sub(r'_{([^}]+)}', convert_sub, text)
            
            # Superíndices simples sin llaves
            text = text.replace('^-1', '⁻¹').replace('^-2', '⁻²').replace('^-3', '⁻³')
            text = text.replace('^1', '¹').replace('^2', '²').replace('^3', '³').replace('^4', '⁴')
            text = text.replace('^2+', '²⁺').replace('^3+', '³⁺')
            
            # Subíndices simples
            text = text.replace('_s', 'ₛ').replace('_w', 'ᵥᵥ').replace('_p', 'ₚ').replace('_2', '₂')
            
            # Ahora limpiar llaves restantes (después de procesar super/subíndices)
            text = text.replace('{', '').replace('}', '')
            text = re.sub(r'\\[a-zA-Z]+', '', text)
            text = text.replace('\\', '')
            
            return text
        
        # PRÁCTICA 1
        if 'p1' in results:
            story.append(Paragraph("PRÁCTICA 1: POTENCIAL OSMÓTICO Y HÍDRICO", heading_style))
            
            # Sacarosa
            if 'sacarosa' in results['p1'] and not results['p1']['sacarosa'].empty:
                story.append(Paragraph("<b>Sacarosa:</b>", small_style))
                df_sac = results['p1']['sacarosa']
                # Limpiar LaTeX en todas las celdas
                table_data = [[clean_latex(str(cell)) for cell in df_sac.columns.tolist()]]
                table_data += [[clean_latex(str(cell)) for cell in row] for row in df_sac.values.tolist()]
                t = Table(table_data, colWidths=[3*cm]*len(df_sac.columns))
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.2*cm))
                if 'sacarosa_expl' in results['p1']:
                    add_text(results['p1']['sacarosa_expl'])
            
            # Cebolla
            if 'onion_fig' in results['p1']:
                story.append(Paragraph("<b>Cebolla - Potencial Osmótico:</b>", small_style))
                add_figure(results['p1']['onion_fig'], width=13*cm, max_height=8*cm)
                if 'onion_pot' in results['p1']:
                    story.append(Paragraph(f"Potencial osmótico: {results['p1']['onion_pot']} MPa", small_style))
                if 'onion_expl' in results['p1']:
                    add_text(results['p1']['onion_expl'])
            
            # Patata
            if 'potato_fig' in results['p1']:
                story.append(Paragraph("<b>Patata - Potencial Hídrico:</b>", small_style))
                add_figure(results['p1']['potato_fig'], width=13*cm, max_height=8*cm)
                if 'potato_pot' in results['p1']:
                    story.append(Paragraph(f"Potencial hídrico: {results['p1']['potato_pot']} MPa", small_style))
                if 'potato_expl' in results['p1']:
                    add_text(results['p1']['potato_expl'])
            
            story.append(PageBreak())
        
        # PRÁCTICA 2
        if 'p2' in results:
            story.append(Paragraph("PRÁCTICA 2: TRANSPIRACIÓN", heading_style))
            
            # Maíz
            if 'corn_fig' in results['p2']:
                story.append(Paragraph("<b>Maíz - Potencial Hídrico:</b>", small_style))
                add_figure(results['p2']['corn_fig'], width=13*cm, max_height=8*cm)
                if 'corn_pot' in results['p2']:
                    story.append(Paragraph(f"Potencial hídrico: {results['p2']['corn_pot']} MPa", small_style))
                if 'corn_expl' in results['p2']:
                    add_text(results['p2']['corn_expl'])
                story.append(Spacer(1, 0.3*cm))
            
            # Guisante
            if 'pea_fig1' in results['p2']:
                story.append(Paragraph("<b>Guisante - Potencial Hídrico:</b>", small_style))
                add_figure(results['p2']['pea_fig1'], width=13*cm, max_height=8*cm)
                if 'pea_pot' in results['p2']:
                    story.append(Paragraph(f"Potencial hídrico: {results['p2']['pea_pot']} MPa", small_style))
                story.append(Spacer(1, 0.3*cm))
            
            if 'pea_fig2' in results['p2']:
                story.append(Paragraph("<b>Guisante - Resistencias:</b>", small_style))
                add_figure(results['p2']['pea_fig2'], width=13*cm, max_height=8*cm)
                if 'pea_expl' in results['p2']:
                    add_text(results['p2']['pea_expl'])
                story.append(Spacer(1, 0.3*cm))
            
            story.append(PageBreak())
        
        # PRÁCTICA 3
        if 'p3' in results:
            story.append(Paragraph("PRÁCTICA 3: CLOROFILAS Y PIGMENTOS", heading_style))
            
            # Clorofila
            if 'clorofila' in results['p3'] and not results['p3']['clorofila'].empty:
                story.append(Paragraph("<b>Determinación de Clorofila:</b>", small_style))
                df_clor = results['p3']['clorofila']
                # Limpiar LaTeX en todas las celdas
                table_data = [[clean_latex(str(cell)) for cell in df_clor.columns.tolist()]]
                table_data += [[clean_latex(str(cell)) for cell in row] for row in df_clor.values.tolist()]
                t = Table(table_data, colWidths=[4*cm]*len(df_clor.columns))
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))
                if 'clor_expl' in results['p3']:
                    add_text(results['p3']['clor_expl'])
            
            # Cromatografía
            if 'cromatografia' in results['p3'] and not results['p3']['cromatografia'].empty:
                story.append(Paragraph("<b>Cromatografía de Pigmentos:</b>", small_style))
                df_crom = results['p3']['cromatografia']
                table_data = [df_crom.columns.tolist()] + df_crom.values.tolist()
                t = Table(table_data, colWidths=[3.5*cm]*len(df_crom.columns))
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))
                if 'croma_expl' in results['p3']:
                    add_text(results['p3']['croma_expl'])
            
            # Anabaena
            if 'anabaena_abs' in results['p3']:
                story.append(Paragraph(f"<b>Anabaena Absorbancia:</b> {results['p3']['anabaena_abs']}", small_style))
                if 'anabaena_expl' in results['p3']:
                    add_text(results['p3']['anabaena_expl'])
                story.append(Spacer(1, 0.3*cm))
            
            story.append(PageBreak())
        
        # PRÁCTICA 4
        if 'p4' in results:
            story.append(Paragraph("PRÁCTICA 4: REACCIÓN DE HILL", heading_style))
            
            # Clorofila Hill
            if 'chl_hill' in results['p4'] and not results['p4']['chl_hill'].empty:
                story.append(Paragraph("<b>Determinación de Clorofila:</b>", small_style))
                df_chl = results['p4']['chl_hill']
                # Limpiar LaTeX en todas las celdas
                table_data = [[clean_latex(str(cell)) for cell in df_chl.columns.tolist()]]
                table_data += [[clean_latex(str(cell)) for cell in row] for row in df_chl.values.tolist()]
                t = Table(table_data, colWidths=[4*cm]*len(df_chl.columns))
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))
                if 'chl_hill_expl' in results['p4']:
                    add_text(results['p4']['chl_hill_expl'])
            
            # Ferricianuro
            if 'ferricianuro' in results['p4'] and not results['p4']['ferricianuro'].empty:
                story.append(Paragraph("<b>Absorción de Ferricianuro:</b>", small_style))
                df_ferri = results['p4']['ferricianuro']
                # Limpiar LaTeX en todas las celdas
                table_data = [[clean_latex(str(cell)) for cell in df_ferri.columns.tolist()]]
                table_data += [[clean_latex(str(cell)) for cell in row] for row in df_ferri.values.tolist()]
                t = Table(table_data, colWidths=[3*cm]*len(df_ferri.columns))
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))
                if 'ferri_expl_pdf' in results['p4']:
                    add_text_simple(results['p4']['ferri_expl_pdf'])
            
            # Hill figura
            if 'hill_fig' in results['p4']:
                story.append(Paragraph("<b>Reacción de Hill:</b>", small_style))
                add_figure(results['p4']['hill_fig'], width=13*cm, max_height=8*cm)
                story.append(Spacer(1, 0.3*cm))
            
            # Fotosíntesis
            if 'fotosintesis' in results['p4'] and not results['p4']['fotosintesis'].empty:
                story.append(Paragraph("<b>Actividades Fotosintéticas:</b>", small_style))
                df_foto = results['p4']['fotosintesis']
                # Limpiar LaTeX en todas las celdas
                table_data = [[clean_latex(str(cell)) for cell in df_foto.columns.tolist()]]
                table_data += [[clean_latex(str(cell)) for cell in row] for row in df_foto.values.tolist()]
                t = Table(table_data, colWidths=[8*cm, 4*cm])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))
                if 'foto_expl_pdf' in results['p4']:
                    add_text_simple(results['p4']['foto_expl_pdf'])
            
            story.append(PageBreak())
        
        # PRÁCTICA 5
        if 'p5' in results:
            story.append(Paragraph("PRÁCTICA 5: GERMINACIÓN Y α-AMILASA", heading_style))
            
            if 'germinacion' in results['p5']:
                story.append(Paragraph(f"<b>Germinación:</b> {results['p5']['germinacion']}%", small_style))
                if 'germ_expl' in results['p5']:
                    add_text(results['p5']['germ_expl'])
                story.append(Spacer(1, 0.3*cm))
            
            # Amilasa figura
            if 'amilasa_fig' in results['p5']:
                story.append(Paragraph("<b>Actividad α-amilasa:</b>", small_style))
                add_figure(results['p5']['amilasa_fig'], width=13*cm, max_height=8*cm)
                story.append(Spacer(1, 0.3*cm))
            
            # Tabla amilasa
            if 'amilasa' in results['p5'] and not results['p5']['amilasa'].empty:
                df_amil = results['p5']['amilasa']
                # Limpiar LaTeX en todas las celdas (solo primeras 5 columnas)
                table_data = [[clean_latex(str(cell)) for cell in df_amil.columns.tolist()[:5]]]
                table_data += [[clean_latex(str(cell)) for cell in row[:5]] for row in df_amil.values.tolist()]
                t = Table(table_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))
                if 'amilasa_expl' in results['p5']:
                    add_text(results['p5']['amilasa_expl'])
            
            story.append(PageBreak())
    
        story.append(PageBreak())
        story.append(Paragraph("CONCLUSIONES", heading_style))
        story.append(Paragraph("Todos los análisis se completaron satisfactoriamente. Consulte el dashboard web para gráficas y explicaciones detalladas.", styles['Normal']))
        
        # Construir el documento
        doc.build(story)
        
        # Ahora sí podemos cerrar los buffers
        for buf in image_buffers:
            try:
                buf.close()
            except:
                pass
        
        print(f"  ✓ PDF generado exitosamente: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"  ✗ Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        # Retornar None si falla
        return None

# ============================================================================
# INTERFAZ GRADIO
# ============================================================================

def create_interface():
    """Crea interfaz Gradio con todas las prácticas y TODOS los outputs"""
    
    with gr.Blocks(title="Dashboard Prácticas - Fisiología Vegetal UAM", theme=gr.themes.Soft()) as demo:
        
        gr.HTML("""
            <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: white; margin: 0; font-size: 2.8em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    🌱 Dashboard de Prácticas Completo
                </h1>
                <h2 style="color: white; margin: 10px 0 0 0; font-weight: normal; font-size: 1.4em;">
                    Fisiología Vegetal
                </h2>
                <p style="color: white; margin: 10px 0 0 0; opacity: 0.95; font-size: 1.1em;">
                    Universidad Autónoma de Madrid (UAM) · 5 Prácticas Completas
                </p>
            </div>
        """)
        
        gr.Markdown("""
            ### 📋 Instrucciones:
            
            1. **📁 Suba su archivo Excel** con los datos completos de las prácticas
            2. **🔬 Haga clic en "Analizar Todo"** para procesar automáticamente las 5 prácticas
            3. **📊 Revise los resultados** en las pestañas correspondientes
            4. **📄 Descargue el informe PDF** con todos los análisis
            
            ---
        """)
        
        with gr.Row():
            file_input = gr.File(label="📁 Subir archivo Excel completo (.xlsx)", file_types=[".xlsx", ".xls"])
        
        with gr.Row():
            process_btn = gr.Button("🔬 Analizar Todo", variant="primary", size="lg", scale=3)
            clear_btn = gr.ClearButton(value="🗑️ Limpiar", size="lg", scale=1)
        
        status_output = gr.HTML(label="📊 Estado del Análisis")
        
        # ===== PRÁCTICA 1 =====
        gr.Markdown("""
        ---
        # 🌱 PRÁCTICA 1: Potencial Osmótico y Hídrico
        ---
        """)
        
        gr.Markdown("### 💧 Sacarosa")
        df_sac_out = gr.Dataframe(label="Tabla de Sacarosa")
        sac_expl_out = gr.Markdown()
        
        gr.Markdown("### 🧅 Cebolla - Plasmólisis")
        df_onion_out = gr.Dataframe(label="Datos de Cebolla")
        fig_onion_out = gr.Plot(label="Gráfica de Plasmólisis")
        onion_expl_out = gr.Markdown()
        
        gr.Markdown("### 🥔 Patata - Potencial Hídrico")
        df_potato_out = gr.Dataframe(label="Datos de Patata")
        fig_potato_out = gr.Plot(label="Variación de Peso")
        potato_expl_out = gr.Markdown()
        
        # ===== PRÁCTICA 2 =====
        gr.Markdown("""
        ---
        # 🌾 PRÁCTICA 2: Auxinas y Estrés Salino
        ---
        """)
        
        gr.Markdown("### 🌽 Maíz - Auxina")
        df_corn_out = gr.Dataframe(label="Datos de Maíz")
        fig_corn_out = gr.Plot(label="Variación de Longitud")
        corn_expl_out = gr.Markdown()
        
        gr.Markdown("### 🌱 Guisante - Estrés Salino")
        df_pea_out = gr.Dataframe(label="Datos de Guisante")
        with gr.Row():
            fig_pea1_out = gr.Plot(label="Variación de Peso")
            fig_pea2_out = gr.Plot(label="Metabolismo (NBT/TFT)")
        pea_expl_out = gr.Markdown()
        
        # ===== PRÁCTICA 3 =====
        gr.Markdown("""
        ---
        # 🍃 PRÁCTICA 3: Clorofilas y Pigmentos
        ---
        """)
        
        gr.Markdown("### 🌿 Clorofila en Espinaca")
        df_clor_out = gr.Dataframe(label="Determinación de Clorofila")
        clor_expl_out = gr.Markdown()
        
        gr.Markdown("### 🎨 Cromatografía de Pigmentos")
        df_croma_out = gr.Dataframe(label="Resultados Cromatografía")
        croma_expl_out = gr.Markdown()
        
        gr.Markdown("### 🔵 Pigmentos en *Anabaena*")
        df_anabaena_out = gr.Dataframe(label="Ficocianina")
        anabaena_expl_out = gr.Markdown()
        
        # ===== PRÁCTICA 4 =====
        gr.Markdown("""
        ---
        # ☀️ PRÁCTICA 4: Reacción de Hill
        ---
        """)
        
        gr.Markdown("### 🌿 Clorofila en Tilacoides")
        df_chl_hill_out = gr.Dataframe(label="Clorofila para Reacción")
        chl_hill_expl_out = gr.Markdown()
        
        gr.Markdown("### 🔬 Concentración de Ferricianuro")
        df_ferri_out = gr.Dataframe(label="Ferricianuro")
        ferri_expl_out = gr.Markdown()
        
        gr.Markdown("### ⚡ Actividad Fotosintética")
        df_hill_out = gr.Dataframe(label="Datos de Hill")
        fig_hill_out = gr.Plot(label="Reducción de Ferricianuro")
        df_foto_out = gr.Dataframe(label="Actividades Calculadas")
        foto_expl_out = gr.Markdown()
        
        # ===== PRÁCTICA 5 =====
        gr.Markdown("""
        ---
        # 🌾 PRÁCTICA 5: Germinación y α-Amilasa
        ---
        """)
        
        gr.Markdown("### 🌱 Germinación de Cebada")
        germ_out = gr.Markdown()
        
        gr.Markdown("### 🧪 Actividad α-Amilasa")
        df_amil_out = gr.Dataframe(label="Datos de α-Amilasa")
        fig_amil_out = gr.Plot(label="Actividad por Tratamiento")
        amil_expl_out = gr.Markdown()
        
        pdf_output = gr.File(label="📄 Descargar Informe PDF Completo")
        
        # CONECTAR TODOS LOS OUTPUTS (35 en total)
        all_outputs = [
            status_output,
            # Práctica 1 (8 outputs)
            df_sac_out, sac_expl_out, 
            df_onion_out, fig_onion_out, onion_expl_out, 
            df_potato_out, fig_potato_out, potato_expl_out,
            # Práctica 2 (7 outputs)
            df_corn_out, fig_corn_out, corn_expl_out, 
            df_pea_out, fig_pea1_out, fig_pea2_out, pea_expl_out,
            # Práctica 3 (6 outputs)
            df_clor_out, clor_expl_out, 
            df_croma_out, croma_expl_out, 
            df_anabaena_out, anabaena_expl_out,
            # Práctica 4 (8 outputs)
            df_chl_hill_out, chl_hill_expl_out, 
            df_ferri_out, ferri_expl_out, 
            df_hill_out, fig_hill_out, 
            df_foto_out, foto_expl_out,
            # Práctica 5 (4 outputs)
            germ_out, 
            df_amil_out, fig_amil_out, amil_expl_out,
            # PDF (1 output)
            pdf_output
        ]
        
        process_btn.click(
            fn=process_all_practicas,
            inputs=[file_input],
            outputs=all_outputs
        )
        
        gr.Markdown("""
            ---
            
            ### ℹ️ Información Técnica:
            
            Este dashboard procesa automáticamente:
            - ✅ **5 Prácticas completas** con tablas y gráficas
            - ✅ **Validación automática** de cálculos (✅/❌)
            - ✅ **Modelos matemáticos** (sigmoide, lineal)
            - ✅ **Explicaciones científicas** con fórmulas
            - ✅ **Informe PDF descargable**
            
            <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f8f9fa; 
                        border-radius: 10px; border-left: 5px solid #667eea;">
                <p style="margin: 0; color: #495057; font-size: 0.95em;">
                    <b>Desarrollado para el Departamento de Fisiología Vegetal</b><br>
                    Universidad Autónoma de Madrid (UAM) · 2026<br>
                    <em>Análisis automático y validación de prácticas de laboratorio</em>
                </p>
            </div>
        """)
    
    return demo

# ============================================================================
# LANZAMIENTO
# ============================================================================

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
