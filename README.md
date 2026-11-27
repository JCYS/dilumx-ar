# DILUMX — Estudio de iluminación AR / POC 01

Web estática, responsive, sin backend. Dos lámparas originales reconstruidas en 3D a partir de las fotografías del catálogo aportado. Dimensiones en metros, eje Y arriba, base en y=0. Las formas, materiales y medidas secundarias son estimaciones; no es CAD certificado. El cable no se modeló y la bombilla interna es ilustrativa (no implica que venga incluida). No hay simulación fotométrica real ni conexión a inventario.

## Ejecutar en tu Mac

1. Descomprime el ZIP y abre la carpeta `dilumx-ar` en VS Code.
2. En esa carpeta: `python3 -m http.server 8080`.
3. Abre `http://localhost:8080` en el navegador. No abras `index.html` con file:// (usa módulos ES).
4. Selecciona Giselle o Emilia, gira y acerca el modelo. Se necesita conexión a Internet para importar model-viewer 4.4.0 desde el CDN de Google.

## Probar AR desde el celular (HTTPS)

**Opción A: GitHub Pages**. Crea un repositorio público vacío, sube el contenido de `dilumx-ar` al directorio raíz (no la carpeta contenedora), activa Settings → Pages → Deploy from a branch → main / (root). Abre la URL HTTPS publicada desde el celular. Los archivos GLB deben estar accesibles sin autenticación para Scene Viewer. No se necesita backend.

**Opción B: Netlify Drop**. Visita https://app.netlify.com/drop y arrastra la carpeta descomprimida `dilumx-ar` (puede requerir cuenta). Abre la URL HTTPS del sitio desde el celular. Alternativamente despliega en Azure Static Web Apps como sitio HTML estático (app_location `/`, sin compilación). Se incluye configuración MIME para Azure.

**Opción C: túnel temporal HTTPS**. Con el servidor local en ejecución y cloudflared instalado: `cloudflared tunnel --url http://localhost:8080`. Abre la URL pública HTTPS que imprime la herramienta. Solo para pruebas: la URL expone temporalmente el contenido servido. No publiques información privada.

- Android: Chrome + dispositivo compatible con ARCore, WebXR o Scene Viewer.
- iPhone: Safari + dispositivo compatible con Quick Look. Model-viewer genera USDZ automáticamente desde GLB (no se incluye USDZ separado).
- Pulsa «Ver en mi espacio» y permite cámara. Apunta a una mesa despejada y bien iluminada. La detección de superficies depende del dispositivo.
- El botón aparece solamente en dispositivos compatibles. Si no aparece, comprueba HTTPS, permisos y compatibilidad. Un iframe o vista previa embebida puede impedir AR; abre la URL directamente.
- `ar-scale="fixed"` mantiene el tamaño del catálogo. `ar-placement="floor"` usa superficies horizontales, no significa que la lámpara sea necesariamente de piso.

## Estructura

```
index.html                 interfaz y componente model-viewer
css/styles.css             diseño responsive
js/products.js             catálogo (fuente de datos)
js/app.js                  selección, giro, estado y eventos AR
assets/models/giselle.glb  0.21 × 0.48 × 0.21 m
assets/models/emilia.glb   0.21 × 0.44 × 0.21 m
assets/images/             fotos del catálogo y pósteres derivados de geometría
 tools/generate_models.py  generador paramétrico de los GLB
 tools/render_previews.py  pósteres de respaldo
```

Para generar nuevamente los GLB y pósteres (opcional): `python3 -m pip install numpy trimesh Pillow` y después `python3 tools/generate_models.py` y `python3 tools/render_previews.py`.

Referencia: https://modelviewer.dev/examples/augmentedreality/index.html y https://modelviewer.dev/docs/.

Pruebas: se verifican los archivos GLB localmente y la interfaz estática; la biblioteca externa y la cámara AR requieren prueba en un navegador y teléfono con acceso a Internet. Esta entrega no incluye alojamiento público.
