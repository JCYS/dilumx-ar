import { products } from './products.js';

// Referencias a elementos de la interfaz. El visor se reutiliza al cambiar de producto.
const $ = id => document.getElementById(id);
const viewer = $('viewer');
const status = $('status');
let selected = products[0];
let ready = false;

// Renderiza el catálogo con botones accesibles y una foto de referencia por producto.
for (const item of products) {
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'product'; button.dataset.id = item.id;
  button.setAttribute('aria-pressed', String(item.id === selected.id));
  button.innerHTML = `<img src="${item.photo}" alt="Foto de catálogo de ${item.name}"><span class="product-info"><small>${item.code}</small><strong>${item.name}</strong><span>${item.price}</span></span><span class="chevron" aria-hidden="true">↗</span>`;
  button.addEventListener('click', () => selectProduct(item));
  $('products').append(button);
}

// Sincroniza los detalles, el archivo GLB, el póster y la selección del catálogo.
function selectProduct(item) {
  if (item.id === selected.id) return;
  selected = item;
  $('name').textContent = item.name;
  $('model').textContent = `MODELO ${item.code}`;
  $('description').textContent = item.description;
  $('price').textContent = item.price;
  $('height').textContent = item.height;
  $('stage-code').textContent = `${item.code} / ${item.name.toUpperCase()}`;
  $('download').href = item.model;
  viewer.setAttribute('alt', `Modelo 3D de la lámpara ${item.name}`);
  viewer.setAttribute('poster', item.poster);
  viewer.setAttribute('src', item.model);
  status.textContent = ready ? 'Cargando modelo…' : 'Cargando visor 3D…';
  document.querySelectorAll('.product').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.id === item.id)));
}

// AR usa el botón slot oficial: solo aparece cuando el visor detecta compatibilidad.
// No se invoca la cámara automáticamente, debe hacerlo el visitante.
viewer.addEventListener('load', () => {
  status.textContent = viewer.canActivateAR ? 'Realidad aumentada disponible en este dispositivo.' : 'Vista 3D disponible. Para AR, abre la web HTTPS en un celular compatible.';
});
viewer.addEventListener('progress', event => {
  const percent = Math.round(event.detail.totalProgress * 100);
  $('progress').style.width = `${percent}%`;
  $('progress').parentElement.hidden = percent >= 100;
});
viewer.addEventListener('error', () => { status.textContent = 'No se pudo cargar el modelo. Revisa tu conexión y vuelve a intentar.'; });
viewer.addEventListener('ar-status', event => {
  if (event.detail.status === 'failed') status.textContent = 'No se pudo iniciar AR. Comprueba los permisos de cámara y la compatibilidad del celular.';
  if (event.detail.status === 'not-presenting' && viewer.loaded) status.textContent = viewer.canActivateAR ? 'Realidad aumentada disponible en este dispositivo.' : 'Vista 3D disponible.';
});
$('rotate').addEventListener('click', () => {
  const enabled = !viewer.hasAttribute('auto-rotate');
  viewer.toggleAttribute('auto-rotate', enabled);
  $('rotate').setAttribute('aria-pressed', String(enabled));
  $('rotate').textContent = enabled ? 'Pausar giro' : 'Activar giro';
});
// Mensaje de contingencia si la librería CDN no se descarga.
customElements.whenDefined('model-viewer').then(() => { ready = true; document.body.classList.add('viewer-ready'); });
setTimeout(() => { if (!ready) status.textContent = 'Visor no disponible: comprueba la conexión a Internet. Se muestra una vista previa estática.'; }, 12000);
