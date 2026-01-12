# 🚀 Instrucciones Paso a Paso para Desplegar el Dashboard

## 📝 Guía Completa para Publicar en Hugging Face Spaces

### Paso 1: Crear cuenta en Hugging Face (2 minutos)

1. Ve a [huggingface.co](https://huggingface.co)
2. Haz clic en "Sign Up" (Registrarse)
3. Completa el registro con tu email
4. Verifica tu email

### Paso 2: Crear un nuevo Space (3 minutos)

1. **Una vez dentro de Hugging Face:**
   - Haz clic en tu foto de perfil (arriba a la derecha)
   - Selecciona "New Space"

2. **Configurar el Space:**
   - **Owner:** Tu usuario (se selecciona automáticamente)
   - **Space name:** `practicas-fisiologia-vegetal` (o el nombre que prefieras)
   - **License:** MIT o Apache 2.0
   - **Select the Space SDK:** Selecciona **Gradio** 
   - **Space hardware:** CPU basic - free (es suficiente y gratis)
   - **Visibility:** Pública (para que los estudiantes accedan sin cuenta)
   
3. **Crear el Space:**
   - Haz clic en "Create Space"
   - Espera a que se cree (tarda unos segundos)

### Paso 3: Subir los archivos (5 minutos)

Tienes todo en la carpeta `dashboard_python/`. Ahora subes los archivos:

#### Método A: Subida mediante interfaz web (recomendado)

1. **En la página de tu Space recién creado:**
   - Verás una sección "Files and versions"
   - Haz clic en "Files"
   - Verás archivos por defecto (como `README.md`, `.gitignore`, etc.)

2. **Subir app.py:**
   - Haz clic en "Add file" → "Upload files"
   - Arrastra o selecciona `app.py` de la carpeta `dashboard_python/`
   - En el cuadro de commit message escribe: "Añadir aplicación principal"
   - Haz clic en "Commit changes to main"

3. **Subir requirements.txt:**
   - Repite el proceso anterior con `requirements.txt`
   - Commit message: "Añadir dependencias"
   - Haz clic en "Commit changes to main"

4. **Actualizar README.md (opcional):**
   - Si quieres personalizar el README que se ve en el Space
   - Haz clic en el archivo README.md existente
   - Haz clic en el icono de editar (lápiz)
   - Copia y pega el contenido de tu `README.md`
   - Commit message: "Actualizar README"
   - Haz clic en "Commit changes to main"

#### Método B: Subida mediante Git (para usuarios avanzados)

```bash
# Configurar Git LFS (solo la primera vez)
git lfs install

# Clonar el repositorio del Space
git clone https://huggingface.co/spaces/TU_USUARIO/practicas-fisiologia-vegetal
cd practicas-fisiologia-vegetal

# Copiar archivos desde tu carpeta
cp "f:/Documents/OneDrive - UAM/Docencia/FV/Practicas/apppracticas/dashboard_python/app.py" .
cp "f:/Documents/OneDrive - UAM/Docencia/FV/Practicas/apppracticas/dashboard_python/requirements.txt" .
cp "f:/Documents/OneDrive - UAM/Docencia/FV/Practicas/apppracticas/dashboard_python/README.md" .

# Hacer commit
git add .
git commit -m "Añadir dashboard de prácticas de fisiología vegetal"

# Subir a Hugging Face
git push
```

### Paso 4: Esperar la construcción (2-3 minutos)

1. **El Space se construirá automáticamente:**
   - Verás un mensaje "Building" con un círculo amarillo girando
   - Hugging Face está instalando las dependencias de `requirements.txt`
   - Luego iniciará la aplicación Gradio

2. **Cuando esté listo:**
   - El círculo se pondrá verde
   - Verás "Running" en verde
   - La aplicación se cargará automáticamente en la página

### Paso 5: Probar la aplicación (2 minutos)

1. **Probar con un archivo de ejemplo:**
   - Sube un archivo Excel de prueba
   - Haz clic en "🔬 Analizar Datos"
   - Verifica que se generan las gráficas
   - Descarga el PDF para comprobar

2. **Si hay errores:**
   - Ve a "Logs" (en la parte superior del Space)
   - Revisa los mensajes de error
   - Normalmente son errores en las rutas de los datos del Excel

### Paso 6: Compartir con los estudiantes

1. **Obtener la URL:**
   - La URL de tu Space será algo como:
     ```
     https://huggingface.co/spaces/TU_USUARIO/practicas-fisiologia-vegetal
     ```

2. **Compartir:**
   - Copia esta URL
   - Compártela con los estudiantes por email, Moodle, etc.
   - Los estudiantes NO necesitan cuenta en Hugging Face
   - Solo necesitan abrir el enlace y subir su Excel

### Paso 7: Personalización opcional

#### Cambiar el título del Space:
1. Ve a "Settings" en tu Space
2. Cambia el "Space title"
3. Guarda cambios

#### Añadir un icono personalizado:
1. En "Settings"
2. Sube una imagen en "Space thumbnail"

#### Hacer el Space privado:
1. En "Settings"
2. Cambia "Visibility" a "Private"
3. Los estudiantes necesitarán cuenta y permisos

## 🎯 Resultado Final

Tendrás una URL pública como esta:

```
https://huggingface.co/spaces/tu-usuario/practicas-fisiologia-vegetal
```

Los estudiantes:
1. Abren el enlace
2. Suben su Excel
3. Hacen clic en "Analizar"
4. Descargan el PDF

**¡Sin instalaciones, sin dependencias, sin problemas!**

## 🆘 Solución de Problemas Comunes

### Problema 1: El Space no arranca
**Síntoma:** Círculo rojo, mensaje "Failed"

**Soluciones:**
- Revisa los logs (botón "Logs")
- Verifica que `requirements.txt` esté bien escrito
- Asegúrate de que `app.py` no tiene errores de sintaxis

### Problema 2: Error al procesar Excel
**Síntoma:** "Error al procesar el archivo"

**Soluciones:**
- Verifica que el Excel tenga la hoja "Practica 1"
- Comprueba que los datos están en las celdas correctas (B17:E23 para cebolla)
- Asegúrate de que los números están como números, no como texto

### Problema 3: No se genera el PDF
**Síntoma:** Las gráficas salen pero el PDF no

**Soluciones:**
- Revisa los logs para ver el error específico
- Puede ser falta de memoria (pero no debería con CPU basic)
- Contacta con soporte de Hugging Face si persiste

### Problema 4: El Space es muy lento
**Síntoma:** Tarda mucho en procesar

**Soluciones:**
- Considera actualizar a CPU basic+ (cuesta poco)
- En Settings → Hardware, cambia a un tier superior
- Los primeros usos pueden ser más lentos (caché)

## 📧 Contacto

Si tienes problemas siguiendo esta guía, puedes:
1. Revisar la documentación de Gradio: [gradio.app/docs](https://gradio.app/docs)
2. Revisar la documentación de Spaces: [huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)

## ✅ Checklist Final

Antes de compartir con estudiantes, verifica:

- [ ] El Space está en "Running" (verde)
- [ ] Has probado subir un Excel de ejemplo
- [ ] Las gráficas se generan correctamente
- [ ] El PDF se descarga sin errores
- [ ] La URL es fácil de recordar y compartir
- [ ] Has documentado cualquier requisito especial del formato Excel

---

**¡Felicidades! Tu dashboard está en línea y listo para usar.**

Los estudiantes ahora pueden acceder 24/7 desde cualquier dispositivo con internet, sin necesidad de instalar nada.
