---
title: Dashboard de Prácticas - Fisiología Vegetal
emoji: 🌱
colorFrom: green
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
license: apache-2.0
---

# 🌱 Dashboard de Prácticas de Fisiología Vegetal

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-4.19-orange.svg)](https://gradio.app/)

Dashboard web interactivo para el análisis automático de datos de prácticas de Fisiología Vegetal de la Universidad Autónoma de Madrid (UAM).

## 📋 Descripción

Esta aplicación permite a los estudiantes subir sus archivos Excel con datos experimentales y obtener automáticamente:

- 📊 **Análisis de plasmólisis en cebolla** - Modelo sigmoide para calcular el potencial osmótico
- 📈 **Análisis de potencial hídrico en patata** - Regresión lineal para determinar el potencial hídrico
- 📄 **Informe PDF profesional** - Con gráficas, resultados e interpretación científica

## 🚀 Despliegue en Hugging Face Spaces

### Opción 1: Mediante la interfaz web (más fácil)

1. **Crear cuenta en Hugging Face:**
   - Ve a [huggingface.co](https://huggingface.co) y crea una cuenta gratuita

2. **Crear un nuevo Space:**
   - Haz clic en tu perfil → "New Space"
   - Nombre: `practicas-fisiologia-vegetal`
   - License: Apache 2.0
   - SDK: **Gradio**
   - Space hardware: CPU basic (gratis)
   - Haz clic en "Create Space"

3. **Subir archivos:**
   - En la página del Space, ve a "Files" → "Add file" → "Upload files"
   - Arrastra estos 3 archivos:
     - `app.py`
     - `requirements.txt`
     - `README.md`
   - Haz clic en "Commit changes to main"

4. **¡Listo!**
   - El Space se construirá automáticamente (tarda 2-3 minutos)
   - Una vez listo, tendrás una URL pública como:
     ```
     https://huggingface.co/spaces/TU_USUARIO/practicas-fisiologia-vegetal
     ```
   - Comparte esta URL con los estudiantes

### Opción 2: Mediante Git (para usuarios avanzados)

```bash
# Clonar el repositorio del Space
git clone https://huggingface.co/spaces/TU_USUARIO/practicas-fisiologia-vegetal
cd practicas-fisiologia-vegetal

# Copiar los archivos
cp path/to/app.py .
cp path/to/requirements.txt .
cp path/to/README.md .

# Hacer commit y push
git add .
git commit -m "Añadir dashboard de prácticas"
git push
```

## 💻 Ejecución local

Si prefieres ejecutar el dashboard en tu ordenador:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

Luego abre tu navegador en `http://localhost:7860`

## 📁 Formato del archivo Excel

El archivo Excel debe tener una hoja llamada **"Practica 1"** con:

### Datos de Cebolla (desde fila 18):
- Columna B: Número de tubo
- Columna C: Concentración (moles/L)
- Columna D: Potencial osmótico (MPa)
- Columna E: Porcentaje de plasmólisis (%)

### Datos de Patata (desde fila 38):
- Columna B: Número de tubo
- Columna C: Concentración (moles/L)
- Columna D: Potencial hídrico (MPa)
- Columna E: Peso inicial (g)
- Columna F: Peso final (g)
- Columna G: Porcentaje de variación de peso (%)

## 🔬 Modelos matemáticos

### Modelo Sigmoide (Cebolla)
```
y = 100 / (1 + exp(-(x - xmid) * scal))
```
Donde:
- `y`: Porcentaje de plasmólisis
- `x`: Potencial osmótico (MPa)
- `xmid`: Punto medio de la curva
- `scal`: Pendiente de la curva

### Regresión Lineal (Patata)
```
y = slope * x + intercept
```
Donde:
- `y`: Variación de peso (%)
- `x`: Potencial hídrico (MPa)
- Potencial hídrico del tejido = -intercept / slope

## 📊 Características

- ✅ Interfaz intuitiva y fácil de usar
- ✅ Procesamiento automático de datos
- ✅ Gráficas profesionales con matplotlib
- ✅ Cálculo automático de potenciales
- ✅ Generación de informes PDF
- ✅ Interpretación científica de resultados
- ✅ Manejo robusto de errores
- ✅ 100% gratuito y sin instalación para estudiantes

## 🛠️ Tecnologías utilizadas

- **Gradio** - Framework para interfaces web interactivas
- **Pandas** - Procesamiento de datos de Excel
- **NumPy & SciPy** - Cálculos matemáticos y ajuste de modelos
- **Matplotlib** - Generación de gráficas
- **ReportLab** - Creación de informes PDF

## 📝 Licencia

Apache 2.0 - Uso libre para fines educativos

## 👥 Autor

Desarrollado para el Departamento de Fisiología Vegetal  
Universidad Autónoma de Madrid (UAM)

## 🆘 Soporte

Para dudas o problemas:
1. Verificar que el archivo Excel tiene el formato correcto
2. Asegurarse de que los datos están en las celdas especificadas
3. Contactar con el departamento de Fisiología Vegetal

---

**Nota:** Este dashboard está optimizado para los formatos de datos específicos de las prácticas de Fisiología Vegetal de la UAM. Para otros usos, puede ser necesario adaptar el código.
