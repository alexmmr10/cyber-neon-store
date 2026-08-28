/**
 * ==============================================================================
 * CYBER NEÓN STORE - CLIENT APPLICATION (app.js)
 * Catálogo, Carrito, Variantes Dinámicas, Cupones & Checkout Automatizado
 * ==============================================================================
 */

// Catálogo Fallback (Modo Demo / Offline)
const CATALOGO_DEMO = [
    {
        nombre: "Hoodie Cyberpunk Oversize",
        descripcion: "Sudadera pesada de algodón premium 450 GSM con capucha holgada y detalles reflectivos neón magenta en mangas y espalda. Acabado impermeable suave.",
        categoria: "HOODIES",
        imagen_url: "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
        sku: "HOOD-CYBER-M",
        talla: "M",
        color: "Negro/Rosa Neón",
        precio: 65.00,
        stock: 25,
        tallas_disponibles: ["M", "L", "XL"]
    },
    {
        nombre: "Camiseta Neon Tech UV",
        descripcion: "Camiseta de algodón peinado de alta densidad con serigrafía fosforescente reactiva a luz ultravioleta. Corte relaxed fit con cuello reforzado.",
        categoria: "CAMISETAS",
        imagen_url: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80",
        sku: "TRET-TECH-L",
        talla: "L",
        color: "Negro/Morado",
        precio: 30.00,
        stock: 30,
        tallas_disponibles: ["S", "M", "L"]
    },
    {
        nombre: "Pantalón Cargo Tactical 2.0",
        descripcion: "Pantalón urbano multibolsillos con correas tácticas ajustables, broches magnéticos y tela ripstop resistente a desgarros.",
        categoria: "PANTALONES",
        imagen_url: "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
        sku: "PANT-CARG-S",
        talla: "S",
        color: "Negro Mate",
        precio: 75.00,
        stock: 18,
        tallas_disponibles: ["S", "M", "L"]
    },
    {
        nombre: "Vestido Neón Noche Cyber",
        descripcion: "Vestido entallado de diseño futurista con líneas de vivo fluorescente y tela elástica modeladora con acabado satinado oscuro.",
        categoria: "VESTIDOS",
        imagen_url: "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80",
        sku: "VEST-NEON-M",
        talla: "M",
        color: "Negro/Morado",
        precio: 45.00,
        stock: 25,
        tallas_disponibles: ["S", "M"]
    },
    {
        nombre: "Chaqueta Reflejante Matrix",
        descripcion: "Chaqueta rompevientos con recubrimiento reflectivo tornasol de alta visibilidad nocturna. Cierres impermeables YKK y forro térmico transpirable.",
        categoria: "HOODIES",
        imagen_url: "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80",
        sku: "CHAK-MAT-XL",
        talla: "XL",
        color: "Gris Tornasol",
        precio: 95.00,
        stock: 15,
        tallas_disponibles: ["M", "L", "XL"]
    },
    {
        nombre: "Jogger Urbano Future Tech",
        descripcion: "Pantalón deportivo ajustado de felpa densa con paneles laterales en verde neón, bolsillos con cremallera termosellada y cordón con topes metálicos.",
        categoria: "PANTALONES",
        imagen_url: "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80",
        sku: "JOGG-FUT-M",
        talla: "M",
        color: "Negro/Verde Neón",
        precio: 50.00,
        stock: 30,
        tallas_disponibles: ["S", "M", "L"]
    },
    {
        nombre: "Top Deportivo Compresión Cyber",
        descripcion: "Top elástico de compresión con diseño ergonómico de soporte medio y líneas geométricas reflectantes. Tejido transpirable de secado ultra rápido.",
        categoria: "CAMISETAS",
        imagen_url: "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&auto=format&fit=crop&q=80",
        sku: "TOP-CYB-S",
        talla: "S",
        color: "Negro/Rosa Neón",
        precio: 25.00,
        stock: 25,
        tallas_disponibles: ["XS", "S", "M"]
    },
    {
        nombre: "Gorra Snapback DarkNet 3D",
        descripcion: "Gorra snapback de visera plana con bordado 3D de alta densidad frontal, pin metálico lateral y cierre ajustable de alta resistencia.",
        categoria: "ACCESORIOS",
        imagen_url: "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=800&auto=format&fit=crop&q=80",
        sku: "GORR-NET-U",
        talla: "Única",
        color: "Negro Total / Cyan",
        precio: 20.00,
        stock: 40,
        tallas_disponibles: ["Única"]
    }
];

// Estado de la Aplicación
let productosGlobales = [];
let carrito = JSON.parse(localStorage.getItem('cyber_neon_cart') || '[]');
let categoriaSeleccionada = 'TODOS';
let cuponActivo = null;
// Configuración de API (Local o Producción en la nube)
const API_BASE_URL = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') 
    ? 'http://127.0.0.1:8000' 
    : (window.__CYBER_API_URL__ || window.location.origin);

// Diccionario de Metadatos de Categoría
function obtenerMetaProducto(prod) {
    const cat = (prod.categoria || 'GENERAL').toUpperCase();
    const map = {
        'HOODIES': { categoria: 'HOODIES', icon: '🧥', colorDot: '#ff007f' },
        'CAMISETAS': { categoria: 'CAMISETAS', icon: '👕', colorDot: '#00f0ff' },
        'PANTALONES': { categoria: 'PANTALONES', icon: '👖', colorDot: '#9d00ff' },
        'VESTIDOS': { categoria: 'VESTIDOS', icon: '👗', colorDot: '#ff007f' },
        'ACCESORIOS': { categoria: 'ACCESORIOS', icon: '🧢', colorDot: '#00ff9f' }
    };
    return map[cat] || { categoria: cat, icon: '⚡', colorDot: '#ffb703' };
}

// 1. CARGA DEL CATÁLOGO DESDE LA API
async function cargarCatalogo(mostrarToastFeedback = false) {
    const statusDot = document.getElementById('server-status-dot');
    const statusText = document.getElementById('server-status-text');

    try {
        const controlador = new AbortController();
        const timeoutId = setTimeout(() => controlador.abort(), 3500);

        const respuesta = await fetch(`${API_BASE_URL}/api/productos`, { signal: controlador.signal });
        clearTimeout(timeoutId);

        if (!respuesta.ok) throw new Error("Status " + respuesta.status);

        productosGlobales = await respuesta.json();
        if (statusDot) statusDot.className = "status-dot";
        if (statusText) statusText.innerText = "Azure PostgreSQL Activo";
        
        if (mostrarToastFeedback) {
            mostrarToast('success', `⚡ Catálogo sincronizado con Azure (${productosGlobales.length} prendas)`);
        }
    } catch (error) {
        console.warn("Backend FastAPI en espera o no disponible. Activando catálogo demo.", error);
        productosGlobales = CATALOGO_DEMO;
        if (statusDot) statusDot.className = "status-dot demo";
        if (statusText) statusText.innerText = "Modo Demo";
        if (mostrarToastFeedback) {
            mostrarToast('warning', 'Operando en modo de respaldo local.');
        }
    }

    // Gestionar Deep Linking (?sku=... o ?categoria=...)
    gestionarDeepLinking();

    filtrarYMostrar();
    actualizarInterfazCarrito();
}

// Auto-sincronización reactiva cuando el usuario vuelve a la pestaña de la tienda
window.addEventListener('focus', () => {
    cargarCatalogo(false);
});

// 2. DEEP LINKING (Instagram Stories & Redes Sociales)
function gestionarDeepLinking() {
    const params = new URLSearchParams(window.location.search);
    const skuParam = params.get('sku');
    const catParam = params.get('categoria');

    if (catParam) {
        const btnCat = document.querySelector(`.tab-btn[data-category="${catParam.toUpperCase()}"]`);
        if (btnCat) filtrarCategoria(catParam.toUpperCase(), btnCat);
    }

    if (skuParam) {
        setTimeout(() => {
            abrirQuickView(skuParam);
        }, 300);
    }
}

// 3. FILTRADO, BÚSQUEDA Y ORDENAMIENTO
function filtrarYMostrar() {
    const textoBuscador = document.getElementById('buscador').value.trim().toLowerCase();
    const criterioOrden = document.getElementById('ordenador').value;
    const btnClear = document.getElementById('btn-clear-search');

    if (btnClear) btnClear.style.display = textoBuscador ? 'block' : 'none';

    let resultado = productosGlobales.filter(prod => {
        const cat = (prod.categoria || 'GENERAL').toUpperCase();
        const coincideCategoria = (categoriaSeleccionada === 'TODOS') || (cat === categoriaSeleccionada);

        const coincideTexto =
            prod.nombre.toLowerCase().includes(textoBuscador) ||
            (prod.color && prod.color.toLowerCase().includes(textoBuscador)) ||
            (prod.talla && prod.talla.toLowerCase().includes(textoBuscador)) ||
            (prod.sku && prod.sku.toLowerCase().includes(textoBuscador)) ||
            (prod.descripcion && prod.descripcion.toLowerCase().includes(textoBuscador)) ||
            (prod.variantes && prod.variantes.some(v => 
                v.sku.toLowerCase().includes(textoBuscador) ||
                v.talla.toLowerCase().includes(textoBuscador) ||
                v.color.toLowerCase().includes(textoBuscador)
            ));

        return coincideCategoria && coincideTexto;
    });

    if (criterioOrden === 'precio-asc') {
        resultado.sort((a, b) => a.precio - b.precio);
    } else if (criterioOrden === 'precio-desc') {
        resultado.sort((a, b) => b.precio - a.precio);
    } else if (criterioOrden === 'nombre-asc') {
        resultado.sort((a, b) => a.nombre.localeCompare(b.nombre));
    } else if (criterioOrden === 'stock-desc') {
        resultado.sort((a, b) => b.stock - a.stock);
    }

    mostrarProductos(resultado);
}

function filtrarCategoria(cat, boton) {
    categoriaSeleccionada = cat;
    document.querySelectorAll('.category-tabs .tab-btn').forEach(btn => btn.classList.remove('active'));
    if (boton) boton.classList.add('active');
    filtrarYMostrar();
}

function limpiarBuscador() {
    const input = document.getElementById('buscador');
    if (input) input.value = '';
    filtrarYMostrar();
}

// 4. RENDERIZADO DEL CATÁLOGO DE PRENDAS ÚNICAS
const tallasSeleccionadasTarjetas = {};

function seleccionarTallaTarjeta(prodId, sku, event) {
    if (event) event.stopPropagation();
    tallasSeleccionadasTarjetas[prodId] = sku;

    const card = document.getElementById(`prod-card-${prodId}`);
    if (!card) return;

    let prod = productosGlobales.find(p => String(p.id) === String(prodId) || p.sku === prodId);
    if (!prod || !prod.variantes) return;

    let v = prod.variantes.find(item => item.sku === sku);
    if (!v) return;

    // Actualizar botones de talla en la tarjeta
    card.querySelectorAll('.size-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.style.background = 'rgba(255,255,255,0.06)';
        btn.style.color = '#fff';
        btn.style.borderColor = 'rgba(255,255,255,0.15)';
        btn.style.boxShadow = 'none';
    });

    const btnActivo = card.querySelector(`[data-sku="${sku}"]`);
    if (btnActivo) {
        btnActivo.classList.add('active');
        btnActivo.style.background = 'var(--neon-cyan)';
        btnActivo.style.color = '#000';
        btnActivo.style.borderColor = 'var(--neon-cyan)';
        btnActivo.style.boxShadow = '0 0 10px var(--neon-cyan-glow)';
    }

    // Actualizar precio en la tarjeta
    const elPrecio = card.querySelector('.precio');
    if (elPrecio) elPrecio.innerText = `$${v.precio.toFixed(2)}`;

    // Actualizar stock pill
    const elStock = card.querySelector('.stock-badge');
    if (elStock) {
        elStock.innerText = `● Stock: ${v.stock} u. (Talla ${v.talla})`;
        elStock.className = `stock-badge ${v.stock <= 5 ? 'low' : ''}`;
    }

    // Actualizar botón de agregar
    const elBtnAdd = card.querySelector('.btn-add-cart');
    if (elBtnAdd) {
        elBtnAdd.innerHTML = `<span>+</span> Agregar (Talla ${v.talla})`;
        elBtnAdd.onclick = (e) => {
            e.stopPropagation();
            agregarAlCarrito(v.sku, v.precio);
        };
    }
}

function mostrarProductos(lista) {
    const contenedor = document.getElementById('contenedor-catalogo');
    const contador = document.getElementById('contador-productos');
    if (!contenedor) return;

    contenedor.innerHTML = '';
    if (contador) contador.innerText = `${lista.length} prenda${lista.length !== 1 ? 's' : ''} disponible${lista.length !== 1 ? 's' : ''}`;

    if (lista.length === 0) {
        contenedor.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-muted);">
                <div style="font-size: 3.5rem; margin-bottom: 12px; opacity: 0.5;">🔍</div>
                <h3 style="color: #fff; margin-bottom: 8px;">No encontramos resultados</h3>
                <p style="font-size: 0.9rem;">Prueba con otros términos de búsqueda o selecciona otra categoría.</p>
                <button onclick="limpiarBuscador(); filtrarCategoria('TODOS', document.querySelector('.tab-btn'))" class="btn-admin" style="margin-top: 18px;">
                    Ver Todo el Catálogo
                </button>
            </div>
        `;
        return;
    }

    lista.forEach((prod, index) => {
        const meta = obtenerMetaProducto(prod);
        const imagen = prod.imagen_url || 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800';
        const vars = prod.variantes && prod.variantes.length > 0 
            ? prod.variantes 
            : [{ sku: prod.sku, talla: prod.talla, color: prod.color, precio: prod.precio, stock: prod.stock }];
        
        const prodId = prod.id || prod.sku;
        const skuSeleccionado = tallasSeleccionadasTarjetas[prodId] || vars[0].sku;
        const varActual = vars.find(v => v.sku === skuSeleccionado) || vars[0];
        const stockBajo = varActual.stock <= 5;

        // Renderizar botones de talla interactivos directamente en la tarjeta
        const tallasHtml = vars.map((v) => {
            const esActiva = v.sku === varActual.sku;
            return `
                <button type="button" 
                        class="size-btn ${esActiva ? 'active' : ''}" 
                        data-sku="${v.sku}"
                        onclick="seleccionarTallaTarjeta('${prodId}', '${v.sku}', event)" 
                        title="Talla ${v.talla}: ${v.stock} u. en stock"
                        style="cursor: pointer; padding: 4px 10px; font-weight: 700; ${esActiva ? 'background: var(--neon-cyan); color: #000; border-color: var(--neon-cyan); box-shadow: 0 0 10px var(--neon-cyan-glow);' : 'background: rgba(255,255,255,0.06); color: #fff;'}">
                    ${v.talla}
                </button>
            `;
        }).join('');

        const card = document.createElement('div');
        card.className = 'producto-card';
        card.id = `prod-card-${prodId}`;
        card.style.animation = `fadeIn 0.4s ease forwards ${index * 0.05}s`;

        card.innerHTML = `
            <div>
                <div class="producto-img-wrapper" onclick="abrirQuickView('${varActual.sku}')" title="Click para ver detalle completo">
                    <span class="badge-category">${meta.categoria}</span>
                    <img src="${imagen}" alt="${prod.nombre}" class="producto-img" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800'">
                    <div class="producto-img-overlay"></div>
                    <button type="button" class="quick-view-btn" onclick="event.stopPropagation(); abrirQuickView('${varActual.sku}')">👁️ Ver Tallas</button>
                </div>
                <div class="producto-info">
                    <h3>${prod.nombre}</h3>
                    <div class="pills-row">
                        <span class="stock-badge ${stockBajo ? 'low' : ''}">
                            ● Stock: ${varActual.stock} u. (Talla ${varActual.talla})
                        </span>
                        <span class="pill-color">
                            <span class="color-dot" style="background: ${meta.colorDot}"></span>
                            ${varActual.color || prod.color || meta.categoria}
                        </span>
                    </div>

                    <div style="margin-top: 8px;">
                        <span style="font-size: 0.74rem; color: var(--neon-cyan); font-family: 'JetBrains Mono'; font-weight: 600;">Tallas disponibles (selecciona una):</span>
                        <div class="size-selector-row" style="margin-top: 6px; flex-wrap: wrap; gap: 6px;">
                            ${tallasHtml}
                        </div>
                    </div>

                    <p class="producto-desc">${prod.descripcion || 'Prenda de alta calidad techwear con diseño neón exclusivo.'}</p>
                </div>
            </div>
            <div class="price-action-row">
                <div class="precio-wrapper">
                    <span class="precio-label">Precio</span>
                    <span class="precio">$${varActual.precio.toFixed(2)}</span>
                </div>
                <button type="button" class="btn-add-cart" onclick="agregarAlCarrito('${varActual.sku}', ${varActual.precio})">
                    <span>+</span> Agregar (Talla ${varActual.talla})
                </button>
            </div>
        `;
        contenedor.appendChild(card);
    });
}

// 5. GESTIÓN DEL CARRITO
function agregarAlCarrito(sku, precio, cantidad = 1) {
    // Buscar la variante específica en cualquiera de los productos
    let prodPadre = null;
    let variante = null;

    for (let p of productosGlobales) {
        if (p.variantes && p.variantes.length > 0) {
            let v = p.variantes.find(item => item.sku === sku);
            if (v) {
                variante = v;
                prodPadre = p;
                break;
            }
        } else if (p.sku === sku) {
            variante = p;
            prodPadre = p;
            break;
        }
    }

    const stockDisponible = variante ? variante.stock : 99;
    const nombrePrenda = prodPadre ? prodPadre.nombre : (variante ? variante.nombre : sku);
    const tallaPrenda = variante ? variante.talla : '';
    const colorPrenda = variante ? variante.color : '';
    const imgPrenda = (variante && variante.imagen_url) || (prodPadre && prodPadre.imagen_url) || 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800';

    let itemExistente = carrito.find(item => item.sku === sku);
    if (itemExistente) {
        if (itemExistente.cantidad + cantidad > stockDisponible) {
            mostrarToast('warning', `Límite de stock alcanzado (${stockDisponible} unidades disponibles en talla ${tallaPrenda})`);
            return;
        }
        itemExistente.cantidad += cantidad;
    } else {
        carrito.push({
            sku: sku,
            cantidad: cantidad,
            precio_unitario: precio,
            nombre: nombrePrenda,
            talla: tallaPrenda,
            color: colorPrenda,
            imagen_url: imgPrenda
        });
    }

    guardarCarrito();
    actualizarInterfazCarrito();
    mostrarToast('success', `¡"${nombrePrenda} (Talla ${tallaPrenda})" agregado al carrito!`);
}

function modificarCantidad(sku, delta) {
    let item = carrito.find(i => i.sku === sku);
    if (!item) return;

    let stockMax = 99;
    for (let p of productosGlobales) {
        if (p.variantes) {
            let v = p.variantes.find(item => item.sku === sku);
            if (v) { stockMax = v.stock; break; }
        } else if (p.sku === sku) {
            stockMax = p.stock;
            break;
        }
    }

    if (delta > 0 && item.cantidad >= stockMax) {
        mostrarToast('warning', `Has alcanzado el stock máximo (${stockMax} u.) de esta prenda`);
        return;
    }

    item.cantidad += delta;
    if (item.cantidad <= 0) {
        eliminarDelCarrito(sku, false);
        return;
    }

    guardarCarrito();
    actualizarInterfazCarrito();
}

function eliminarDelCarrito(sku, notificar = true) {
    carrito = carrito.filter(item => item.sku !== sku);
    guardarCarrito();
    actualizarInterfazCarrito();
    if (notificar) mostrarToast('info', 'Prenda retirada del carrito');
}

function vaciarCarrito() {
    if (carrito.length === 0) return;
    if (confirm('¿Deseas vaciar todos los artículos de tu carrito?')) {
        carrito = [];
        guardarCarrito();
        actualizarInterfazCarrito();
        mostrarToast('info', 'Carrito vaciado');
    }
}

function guardarCarrito() {
    localStorage.setItem('cyber_neon_cart', JSON.stringify(carrito));
}

// 8. MODAL DE VISTA RÁPIDA (QUICK VIEW) CON SELECTOR REACTIVO DE TALLAS
let productoModalActual = null;
let varianteModalActual = null;

function abrirQuickView(sku) {
    let prod = null;
    let varInicial = null;

    for (let p of productosGlobales) {
        if (p.variantes && p.variantes.length > 0) {
            let v = p.variantes.find(item => item.sku === sku);
            if (v) {
                prod = p;
                varInicial = v;
                break;
            }
        }
        if (p.sku === sku || String(p.id) === String(sku)) {
            prod = p;
            varInicial = (p.variantes && p.variantes.length > 0) ? p.variantes[0] : p;
            break;
        }
    }

    if (!prod) return;
    if (!varInicial) varInicial = (prod.variantes && prod.variantes.length > 0) ? prod.variantes[0] : prod;

    productoModalActual = prod;
    varianteModalActual = varInicial;

    renderizarContenidoQuickView();
    const modal = document.getElementById('quick-view-modal');
    if (modal) modal.style.display = 'flex';
}

function cambiarTallaModal(sku) {
    if (!productoModalActual || !productoModalActual.variantes) return;
    const v = productoModalActual.variantes.find(item => item.sku === sku);
    if (!v) return;
    varianteModalActual = v;
    renderizarContenidoQuickView();
}

function renderizarContenidoQuickView() {
    const content = document.getElementById('quick-view-content');
    if (!content || !productoModalActual || !varianteModalActual) return;

    const prod = productoModalActual;
    const vActiva = varianteModalActual;
    const meta = obtenerMetaProducto(prod);
    const img = vActiva.imagen_url || prod.imagen_url || 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800';
    const variantes = prod.variantes && prod.variantes.length > 0 
        ? prod.variantes 
        : [{ sku: prod.sku, talla: prod.talla, color: prod.color, precio: prod.precio, stock: prod.stock }];

    // Renderizar botones de selección de talla con estilo cyberpunk y feedback inmediato
    let tallasSelectorHtml = '<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px;">';
    variantes.forEach(v => {
        const esActiva = v.sku === vActiva.sku;
        const sinStock = v.stock <= 0;
        tallasSelectorHtml += `
            <button type="button" 
                    class="size-btn ${esActiva ? 'active' : ''} ${sinStock ? 'disabled' : ''}" 
                    onclick="cambiarTallaModal('${v.sku}')"
                    style="padding: 10px 18px; font-size: 0.95rem; font-weight: 800; border-radius: 8px; cursor: pointer; transition: all 0.2s ease; ${esActiva ? 'background: var(--neon-cyan); color: #000; box-shadow: 0 0 15px var(--neon-cyan-glow); border: 1px solid var(--neon-cyan);' : 'background: rgba(255,255,255,0.06); color: #fff; border: 1px solid rgba(255,255,255,0.2);'} ${sinStock ? 'opacity: 0.35; text-decoration: line-through; cursor: not-allowed;' : ''}">
                ${v.talla} ${sinStock ? '(Agotado)' : ''}
            </button>
        `;
    });
    tallasSelectorHtml += '</div>';

    const sinStockActivo = vActiva.stock <= 0;
    const stockBajo = vActiva.stock > 0 && vActiva.stock <= 5;
    const stockColor = sinStockActivo ? 'var(--neon-pink)' : (stockBajo ? 'var(--neon-amber)' : 'var(--neon-green)');
    const stockTexto = sinStockActivo 
        ? `❌ Agotado en talla ${vActiva.talla}` 
        : (stockBajo 
            ? `⚠️ Solo ${vActiva.stock} unidades en talla ${vActiva.talla}` 
            : `● ${vActiva.stock} unidades disponibles en talla ${vActiva.talla}`);

    content.innerHTML = `
        <div style="display: flex; gap: 24px; flex-wrap: wrap; align-items: start;">
            <div style="width: 250px; height: 280px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-neon); box-shadow: 0 0 25px var(--neon-purple-glow); flex-shrink: 0;">
                <img src="${img}" alt="${prod.nombre}" style="width:100%; height:100%; object-fit:cover;">
            </div>
            <div style="flex: 1; min-width: 270px;">
                <span class="badge-category">${meta.categoria}</span>
                <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.55rem; color: #fff; margin-top: 8px; line-height: 1.2;">${prod.nombre}</h2>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: var(--neon-cyan); margin: 6px 0 12px;">
                    SKU: <b>${vActiva.sku}</b>
                </p>
                
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 12px 14px; border-radius: 10px; margin-bottom: 14px;">
                    <p style="font-size: 0.88rem; line-height: 1.45; color: #e2e8f0;">${prod.descripcion || 'Prenda exclusiva techwear con diseño neón reflectante.'}</p>
                </div>

                <!-- Selector de Tallas Interactivo -->
                <div style="background: rgba(0,0,0,0.4); border: 1px solid rgba(0,240,255,0.25); border-radius: 10px; padding: 12px 14px; margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                        <label style="font-size: 0.74rem; color: var(--neon-cyan); text-transform: uppercase; font-family: 'JetBrains Mono'; font-weight: 700;">
                            Selecciona tu Talla:
                        </label>
                        <span style="font-size: 0.74rem; color: #fff; font-family: 'JetBrains Mono';">Talla elegida: <b style="color: var(--neon-cyan);">${vActiva.talla}</b></span>
                    </div>
                    ${tallasSelectorHtml}
                </div>

                <!-- Indicadores de Disponibilidad en Tiempo Real -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 18px;">
                    <div style="background: rgba(0,0,0,0.4); padding: 9px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                        <span style="font-size: 0.70rem; color: var(--text-muted); text-transform: uppercase; display: block;">Stock en Talla ${vActiva.talla}</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: ${stockColor}; font-family: 'JetBrains Mono', monospace; margin-top: 2px;">
                            ${stockTexto}
                        </div>
                    </div>
                    <div style="background: rgba(0,0,0,0.4); padding: 9px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                        <span style="font-size: 0.70rem; color: var(--text-muted); text-transform: uppercase; display: block;">Color / Acabado</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 6px; margin-top: 2px;">
                            <span class="color-dot" style="background: ${meta.colorDot}"></span>
                            ${vActiva.color || prod.color || 'Neón'}
                        </div>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 14px;">
                    <div>
                        <span style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Precio</span>
                        <div class="precio" style="font-size: 1.8rem;">$${vActiva.precio.toFixed(2)}</div>
                    </div>
                    <button type="button" class="btn-comprar" style="padding: 12px 24px; font-size: 0.92rem; ${sinStockActivo ? 'opacity:0.4; cursor:not-allowed;' : ''}" 
                            ${sinStockActivo ? 'disabled' : ''}
                            onclick="agregarAlCarrito('${vActiva.sku}', ${vActiva.precio}); cerrarQuickView();">
                        <span>🛒</span> ${sinStockActivo ? 'Agotado en esta talla' : `Agregar al Carrito (Talla ${vActiva.talla})`}
                    </button>
                </div>
            </div>
        </div>
    `;
}

function cerrarQuickView() {
    const modal = document.getElementById('quick-view-modal');
    if (modal) modal.style.display = 'none';
}

function cerrarModalFuera(e) {
    if (e && e.target && e.target.id === 'quick-view-modal') {
        cerrarQuickView();
    }
}
function actualizarInterfazCarrito() {
    const divItems = document.getElementById('items-carrito');
    const spanSubtotal = document.getElementById('cart-subtotal');
    const spanTotal = document.getElementById('total');
    const spanShipping = document.getElementById('cart-shipping');
    const badgeCount = document.getElementById('cart-badge-count');
    const mobileCount = document.getElementById('mobile-cart-count');
    const shippingFill = document.getElementById('shipping-progress-fill');
    const shippingMsg = document.getElementById('shipping-status-msg');
    const shippingPerc = document.getElementById('shipping-percentage');

    let totalItems = carrito.reduce((acc, item) => acc + item.cantidad, 0);
    if (badgeCount) badgeCount.innerText = totalItems;
    if (mobileCount) mobileCount.innerText = totalItems;

    if (carrito.length === 0) {
        if (divItems) {
            divItems.innerHTML = `
                <div class="empty-cart-state">
                    <div class="empty-cart-icon">🛍️</div>
                    <p>Tu carrito está vacío</p>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">¡Explora la tienda y agrega tus prendas favoritas!</span>
                </div>
            `;
        }
        if (spanSubtotal) spanSubtotal.innerText = '$0.00';
        if (spanTotal) spanTotal.innerText = '0.00';
        if (spanShipping) spanShipping.innerText = '$0.00';
        if (shippingFill) shippingFill.style.width = '0%';
        if (shippingPerc) shippingPerc.innerText = '0%';
        if (shippingMsg) shippingMsg.innerHTML = `Agrega $${METAS_ENVIO_GRATIS.toFixed(2)} para <b>Envío Gratis</b>`;
        const rowDesc = document.getElementById('row-descuento');
        if (rowDesc) rowDesc.style.display = 'none';
        return;
    }

    if (divItems) divItems.innerHTML = '';
    let subtotal = 0;

    carrito.forEach(item => {
        const prod = productosGlobales.find(p => p.sku === item.sku);
        const nombre = prod ? prod.nombre : (item.nombre || item.sku);
        const sub = item.cantidad * item.precio_unitario;
        const img = item.imagen_url || (prod ? prod.imagen_url : 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800');
        subtotal += sub;

        const itemCard = document.createElement('div');
        itemCard.className = 'cart-item-card';
        itemCard.innerHTML = `
            <img src="${img}" alt="${nombre}" class="cart-item-img" onerror="this.src='https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800'">
            <div class="cart-item-details">
                <div class="cart-item-title" title="${nombre}">${nombre}</div>
                <div class="cart-item-meta">
                    <span>${item.sku}</span>
                    ${item.talla ? `<span>• Talla ${item.talla}</span>` : ''}
                </div>
                <div class="cart-item-price">$${sub.toFixed(2)} <span style="font-size: 0.7rem; color: var(--text-muted); font-weight: normal;">($${item.precio_unitario.toFixed(2)} c/u)</span></div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                <button class="btn-remove-item" onclick="eliminarDelCarrito('${item.sku}')" title="Eliminar">🗑️</button>
                <div class="cart-qty-controls">
                    <button class="qty-btn" onclick="modificarCantidad('${item.sku}', -1)">-</button>
                    <span class="qty-number">${item.cantidad}</span>
                    <button class="qty-btn" onclick="modificarCantidad('${item.sku}', 1)">+</button>
                </div>
            </div>
        `;
        if (divItems) divItems.appendChild(itemCard);
    });

    // Barra de Envío Gratis
    const porcentajeEnvio = Math.min(100, Math.round((subtotal / METAS_ENVIO_GRATIS) * 100));
    if (shippingFill) shippingFill.style.width = `${porcentajeEnvio}%`;
    if (shippingPerc) shippingPerc.innerText = `${porcentajeEnvio}%`;

    let envio = 0;
    if (subtotal >= METAS_ENVIO_GRATIS) {
        if (shippingMsg) shippingMsg.innerHTML = `🎉 ¡Felicidades! Tienes <b>Envío GRATIS</b>`;
        if (spanShipping) spanShipping.innerHTML = `<span style="color: var(--neon-green); font-weight:bold;">GRATIS</span>`;
        envio = 0;
    } else {
        const restante = (METAS_ENVIO_GRATIS - subtotal).toFixed(2);
        if (shippingMsg) shippingMsg.innerHTML = `Faltan <b>$${restante}</b> para <b>Envío Gratis</b>`;
        envio = COSTO_ENVIO_ESTANDAR;
        if (spanShipping) spanShipping.innerText = `$${envio.toFixed(2)}`;
    }

    // Descuentos
    let descuento = 0;
    const rowDescuento = document.getElementById('row-descuento');
    const spanDiscount = document.getElementById('cart-discount');

    if (cuponActivo) {
        if (cuponActivo.tipo === 'porcentaje') {
            descuento = subtotal * cuponActivo.valor;
        } else if (cuponActivo.tipo === 'envio') {
            envio = 0;
            if (spanShipping) spanShipping.innerHTML = `<span style="color: var(--neon-green); font-weight:bold;">GRATIS (Cupón)</span>`;
        }
        if (rowDescuento) rowDescuento.style.display = 'flex';
        if (spanDiscount) spanDiscount.innerText = `-$${descuento.toFixed(2)}`;
    } else {
        if (rowDescuento) rowDescuento.style.display = 'none';
    }

    const totalFinal = Math.max(0, subtotal - descuento + envio);
    if (spanSubtotal) spanSubtotal.innerText = `$${subtotal.toFixed(2)}`;
    if (spanTotal) spanTotal.innerText = totalFinal.toFixed(2);
}

// 7. SISTEMA DE CUPONES CON VALIDACIÓN VÍA API
async function aplicarCupon() {
    const input = document.getElementById('coupon-code');
    if (!input) return;
    const codigo = input.value.trim().toUpperCase();
    const container = document.getElementById('active-coupon-container');

    if (!codigo) {
        mostrarToast('warning', 'Ingresa un código de cupón');
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/api/cupones/${codigo}`);
        if (res.ok) {
            const data = await res.json();
            cuponActivo = {
                codigo: data.codigo,
                tipo: data.tipo,
                valor: data.valor,
                desc: data.descripcion
            };
            mostrarToast('success', `¡Cupón ${cuponActivo.codigo} aplicado!`);
        } else {
            throw new Error("Cupón no encontrado");
        }
    } catch (e) {
        // Fallback local
        if (codigo === 'NEON10') {
            cuponActivo = { codigo: 'NEON10', tipo: 'porcentaje', valor: 0.10, desc: '10% de Descuento Especial' };
        } else if (codigo === 'CYBER20') {
            cuponActivo = { codigo: 'CYBER20', tipo: 'porcentaje', valor: 0.20, desc: '20% Cyberpunk VIP' };
        } else if (codigo === 'ENVIOGRATIS') {
            cuponActivo = { codigo: 'ENVIOGRATIS', tipo: 'envio', valor: 0, desc: 'Envío Gratis Garantizado' };
        } else {
            mostrarToast('warning', 'Cupón inválido o caducado');
            return;
        }
        mostrarToast('success', `¡Cupón ${cuponActivo.codigo} activado!`);
    }

    if (container && cuponActivo) {
        container.innerHTML = `
            <div class="active-coupon-tag">
                <span>🎟️ <b>${cuponActivo.codigo}</b>: ${cuponActivo.desc}</span>
                <span style="cursor: pointer; font-weight:bold;" onclick="quitarCupon()">✕</span>
            </div>
        `;
    }

    input.value = '';
    actualizarInterfazCarrito();
}

function quitarCupon() {
    cuponActivo = null;
    const container = document.getElementById('active-coupon-container');
    if (container) container.innerHTML = '';
    actualizarInterfazCarrito();
    mostrarToast('info', 'Cupón removido');
}

// 8. MODAL DE VISTA RÁPIDA (QUICK VIEW)
function abrirQuickView(sku) {
    const prod = productosGlobales.find(p => p.sku === sku);
    if (!prod) return;

    const meta = obtenerMetaProducto(prod);
    const modal = document.getElementById('quick-view-modal');
    const content = document.getElementById('quick-view-content');
    const img = prod.imagen_url || 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800';

    if (content) {
        content.innerHTML = `
            <div style="display: flex; gap: 24px; flex-wrap: wrap; align-items: start;">
                <div style="width: 240px; height: 260px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-neon); box-shadow: 0 0 25px var(--neon-purple-glow);">
                    <img src="${img}" alt="${prod.nombre}" style="width:100%; height:100%; object-fit:cover;">
                </div>
                <div style="flex: 1; min-width: 260px;">
                    <span class="badge-category">${meta.categoria}</span>
                    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; color: #fff; margin-top: 8px;">${prod.nombre}</h2>
                    <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: var(--neon-cyan); margin-bottom: 12px;">SKU: ${prod.sku}</p>
                    
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 14px; border-radius: 10px; margin-bottom: 16px;">
                        <p style="font-size: 0.92rem; line-height: 1.5; color: #e2e8f0;">${prod.descripcion || 'Prenda exclusiva con acabados neón de alta resistencia.'}</p>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                        <div style="background: rgba(0,0,0,0.4); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                            <span style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Talla</span>
                            <div style="font-size: 1.1rem; font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace;">${prod.talla}</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.4); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                            <span style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Color / Acabado</span>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 6px;">
                                <span class="color-dot" style="background: ${meta.colorDot}"></span>
                                ${prod.color}
                            </div>
                        </div>
                    </div>

                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Precio</span>
                            <div class="precio" style="font-size: 2rem;">$${prod.precio.toFixed(2)}</div>
                        </div>
                        <button class="btn-comprar" style="padding: 12px 24px;" onclick="agregarAlCarrito('${prod.sku}', ${prod.precio}); cerrarQuickView();">
                            <span>🛒</span> Agregar al Carrito
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    if (modal) modal.style.display = 'flex';
}

function cerrarQuickView() {
    const modal = document.getElementById('quick-view-modal');
    if (modal) modal.style.display = 'none';
}

function cerrarModalFuera(e) {
    if (e.target.id === 'quick-view-modal') cerrarQuickView();
    if (e.target.id === 'ticket-modal') cerrarTicketModal();
}

function toggleMobileCart() {
    const sidebar = document.getElementById('carrito-sidebar');
    if (sidebar) sidebar.classList.toggle('open');
}

// 9. SISTEMA DE NOTIFICACIONES TOAST
function mostrarToast(tipo, mensaje) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-item ${tipo}`;

    let icon = '⚡';
    if (tipo === 'success') icon = '✅';
    if (tipo === 'warning') icon = '⚠️';
    if (tipo === 'info') icon = 'ℹ️';

    toast.innerHTML = `<span>${icon}</span> <span>${mensaje}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 4000);
}

// 10. GENERACIÓN DEL TICKET DE COMPRA OFICIAL
function generarYMostrarTicket(orderData) {
    const modal = document.getElementById('ticket-modal');
    const content = document.getElementById('ticket-modal-content');
    if (!modal || !content) return;

    const orderId = orderData.order_id;
    const telefono = orderData.telefono;
    const total = orderData.total;
    const subtotal = orderData.subtotal;
    const descuento = orderData.descuento || 0;
    const envio = orderData.envio || 0;
    const items = orderData.items || [];
    const fechaHora = new Date().toLocaleString('es-EC', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });

    let itemsHtml = '';
    items.forEach(item => {
        const prod = productosGlobales.find(p => p.sku === item.sku);
        const nombre = prod ? prod.nombre : (item.nombre || item.sku);
        const talla = prod ? prod.talla : (item.talla || '-');
        const subItem = item.cantidad * item.precio_unitario;

        itemsHtml += `
            <tr>
                <td>
                    <b>${nombre}</b><br>
                    <span style="font-size:0.72rem; color: var(--text-muted); font-family:'JetBrains Mono';">${item.sku} | Talla: ${talla}</span>
                </td>
                <td style="text-align: center; font-family:'JetBrains Mono';">${item.cantidad}</td>
                <td style="text-align: right; font-family:'JetBrains Mono';">$${item.precio_unitario.toFixed(2)}</td>
                <td style="text-align: right; font-weight: bold; color: var(--neon-pink); font-family:'JetBrains Mono';">$${subItem.toFixed(2)}</td>
            </tr>
        `;
    });

    content.innerHTML = `
        <div class="ticket-header">
            <div class="ticket-brand">⚡ CYBER NEÓN STORE</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase;">
                Comprobante de Venta Oficial • Techwear Apparel
            </div>
            <div class="ticket-badge-success">
                <span>✅</span> ORDEN CONFIRMADA
            </div>
        </div>

        <div class="ticket-integration-alert">
            <span style="font-size: 1.4rem;">📲</span>
            <div>
                <b>¡Ticket despachado a tu WhatsApp!</b><br>
                <span style="font-size: 0.72rem; opacity: 0.9;">
                    Enviado mediante <b>n8n</b> & <b>Meta Developers Cloud API</b> al: <b>${telefono}</b>
                </span>
            </div>
        </div>

        <div class="ticket-meta-grid">
            <div class="ticket-meta-item">
                <span class="label">Folio / No. Orden</span>
                <span class="value highlight">${orderId}</span>
            </div>
            <div class="ticket-meta-item">
                <span class="label">Fecha y Hora</span>
                <span class="value">${fechaHora}</span>
            </div>
            <div class="ticket-meta-item">
                <span class="label">WhatsApp Cliente</span>
                <span class="value">${telefono}</span>
            </div>
            <div class="ticket-meta-item">
                <span class="label">Estado de Pago</span>
                <span class="value" style="color: var(--neon-green);">PENDIENTE / CONTRA-ENTREGA</span>
            </div>
        </div>

        <table class="ticket-table">
            <thead>
                <tr>
                    <th>Prenda</th>
                    <th style="text-align: center;">Cant</th>
                    <th style="text-align: right;">Precio</th>
                    <th style="text-align: right;">Subtotal</th>
                </tr>
            </thead>
            <tbody>
                ${itemsHtml}
            </tbody>
        </table>

        <div class="ticket-totals-section">
            <div class="ticket-total-row">
                <span>Subtotal:</span>
                <span style="font-family:'JetBrains Mono';">$${subtotal.toFixed(2)}</span>
            </div>
            ${descuento > 0 ? `
            <div class="ticket-total-row" style="color: var(--neon-green);">
                <span>Descuento (${cuponActivo ? cuponActivo.codigo : 'Cupón'}):</span>
                <span style="font-family:'JetBrains Mono';">-$${descuento.toFixed(2)}</span>
            </div>` : ''}
            <div class="ticket-total-row">
                <span>Costo de Envío:</span>
                <span style="font-family:'JetBrains Mono';">${envio === 0 ? '<b style="color:var(--neon-green)">GRATIS</b>' : '$' + envio.toFixed(2)}</span>
            </div>
            <div class="ticket-total-final">
                <span>TOTAL FACTURADO:</span>
                <span class="amount">$${total.toFixed(2)} USD</span>
            </div>
        </div>

        <div class="ticket-barcode-wrapper">
            <div class="ticket-barcode-lines">||| | |||| || | ||| |||| | || | |||</div>
            <div class="ticket-barcode-number">* ${orderId} *</div>
        </div>

        <div class="ticket-actions">
            <button class="btn-ticket-print" onclick="window.print()">
                <span>🖨️</span> Imprimir / PDF
            </button>
            <button class="btn-ticket-whatsapp" onclick="abrirWhatsAppConDetalles('${telefono}', '${orderId}', ${total})">
                <span>💬</span> Abrir en WhatsApp
            </button>
        </div>
    `;

    modal.style.display = 'flex';
}

function cerrarTicketModal() {
    const modal = document.getElementById('ticket-modal');
    if (modal) modal.style.display = 'none';
}

// 11. CHECKOUT Y ENVÍO DE ORDEN
async function procesarCompra() {
    if (carrito.length === 0) {
        mostrarToast('warning', 'Agrega prendas al carrito primero');
        return;
    }

    const prefijo = document.getElementById('pais-prefijo').value;
    let telefono = document.getElementById('telefono').value.trim();

    if (!telefono) {
        mostrarToast('warning', 'Por favor ingresa tu número de WhatsApp');
        document.getElementById('telefono').focus();
        return;
    }

    telefono = telefono.replace(/[^0-9]/g, '');
    if (telefono.startsWith('0')) telefono = telefono.substring(1);
    const telefonoCompleto = prefijo + telefono;

    const total = parseFloat(document.getElementById('total').innerText);
    let subtotal = 0;
    carrito.forEach(i => subtotal += (i.cantidad * i.precio_unitario));

    let descuento = 0;
    if (cuponActivo && cuponActivo.tipo === 'porcentaje') {
        descuento = subtotal * cuponActivo.valor;
    }
    const envio = subtotal >= METAS_ENVIO_GRATIS ? 0 : COSTO_ENVIO_ESTANDAR;
    const itemsRespaldo = [...carrito];

    const payload = {
        telefono_cliente: telefonoCompleto,
        pais: prefijo.replace('+', ''),
        total_usd: total,
        subtotal_usd: subtotal,
        descuento_usd: descuento,
        envio_usd: envio,
        cupon_codigo: cuponActivo ? cuponActivo.codigo : null,
        metodo_pago: "WhatsApp / Contraentrega",
        items: carrito.map(i => ({
            sku: i.sku,
            cantidad: i.cantidad,
            precio_unitario: i.precio_unitario,
            nombre: i.nombre || i.sku,
            talla: i.talla || "-",
            color: i.color || "-"
        }))
    };

    mostrarToast('info', 'Procesando orden con el servidor...');

    try {
        const respuesta = await fetch(`${API_BASE_URL}/api/orders/checkout`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (respuesta.ok) {
            const data = await respuesta.json();
            const orderId = data.order_id || ('ORD-' + Math.floor(100000 + Math.random() * 900000));

            mostrarToast('success', `¡Orden ${orderId} procesada! Generando ticket...`);

            generarYMostrarTicket({
                order_id: orderId,
                telefono: telefonoCompleto,
                total: total,
                subtotal: subtotal,
                descuento: descuento,
                envio: envio,
                items: itemsRespaldo
            });

            carrito = [];
            guardarCarrito();
            actualizarInterfazCarrito();
            cargarCatalogo();
        } else {
            const errData = await respuesta.json().catch(() => ({}));
            mostrarToast('warning', errData.detail || "Error al procesar la orden.");
        }
    } catch (error) {
        console.warn("Backend local offline. Generando Ticket en modo autónomo:", error);
        const orderIdDemo = 'ORD-' + Math.floor(100000 + Math.random() * 900000);
        mostrarToast('success', `¡Ticket generado (${orderIdDemo})!`);

        generarYMostrarTicket({
            order_id: orderIdDemo,
            telefono: telefonoCompleto,
            total: total,
            subtotal: subtotal,
            descuento: descuento,
            envio: envio,
            items: itemsRespaldo
        });

        carrito = [];
        guardarCarrito();
        actualizarInterfazCarrito();
    }
}

function checkoutDirectoWhatsApp() {
    if (carrito.length === 0) {
        mostrarToast('warning', 'Agrega prendas al carrito primero');
        return;
    }

    const prefijo = document.getElementById('pais-prefijo').value;
    let telefono = document.getElementById('telefono').value.trim();
    telefono = telefono.replace(/[^0-9]/g, '');
    if (telefono.startsWith('0')) telefono = telefono.substring(1);
    const telefonoCompleto = telefono ? (prefijo + telefono) : '';
    const total = parseFloat(document.getElementById('total').innerText);
    const orderId = 'ORD-' + Math.floor(100000 + Math.random() * 900000);

    abrirWhatsAppConDetalles(telefonoCompleto, orderId, total);
}

function abrirWhatsAppConDetalles(telefonoCliente, orderId, total) {
    let mensaje = `⚡ *NUEVA ORDEN - TIENDA CYBER NEÓN*\n`;
    mensaje += `🔖 *Orden ID:* ${orderId}\n`;
    if (telefonoCliente) mensaje += `📱 *Cliente:* ${telefonoCliente}\n`;
    mensaje += `------------------------------------\n`;
    mensaje += `🛍️ *PRENDAS:*\n`;

    const itemsAEnviar = carrito.length > 0 ? carrito : [];
    itemsAEnviar.forEach(item => {
        const prod = productosGlobales.find(p => p.sku === item.sku);
        const nombre = prod ? prod.nombre : (item.nombre || item.sku);
        mensaje += `• *${nombre}* (${item.sku})\n  Cant: ${item.cantidad} x $${item.precio_unitario.toFixed(2)} = $${(item.cantidad * item.precio_unitario).toFixed(2)}\n`;
    });

    mensaje += `------------------------------------\n`;
    if (cuponActivo) mensaje += `🎟️ *Cupón:* ${cuponActivo.codigo}\n`;
    mensaje += `💰 *TOTAL:* $${total.toFixed(2)} USD\n`;
    mensaje += `\n¡Hola! He generado mi pedido en la tienda. Deseo coordinar el pago y la entrega. ✨`;

    const numeroDestino = telefonoCliente.replace('+', '') || '593999999999';
    const urlWhatsApp = `https://wa.me/${numeroDestino}?text=${encodeURIComponent(mensaje)}`;
    window.open(urlWhatsApp, '_blank');
}

// ==============================================================================
// 12. ASISTENTE IA DE ESTILO NEÓN (CYBER STYLIST AI)
// ==============================================================================
let historialChatIA = [];

function toggleAIChat() {
    const chatWin = document.getElementById('ai-chat-window');
    if (!chatWin) return;
    
    const isVisible = chatWin.style.display === 'flex';
    chatWin.style.display = isVisible ? 'none' : 'flex';
    
    if (!isVisible) {
        const input = document.getElementById('ai-chat-input');
        if (input) input.focus();
        // Mensaje de bienvenida inicial si está vacío
        const chatBody = document.getElementById('ai-chat-body');
        if (chatBody && chatBody.children.length === 0) {
            agregarBurbujaBot(
                "⚡ **¡Hola! Soy Cyber Stylist Neón.**\n\n" +
                "Tu asesor de moda cyberpunk y techwear impulsado por **ChatGPT Sol**. ¿Qué estilo buscas hoy o para qué ocasión quieres armar tu outfit?",
                [
                    {
                        nombre: "Hoodie Cyberpunk Oversize",
                        sku: "HOOD-CYBER-M",
                        precio: 65.00,
                        imagen_url: "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800"
                    },
                    {
                        nombre: "Pantalón Cargo Tactical 2.0",
                        sku: "PANT-CARG-S",
                        precio: 75.00,
                        imagen_url: "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800"
                    }
                ],
                "ChatGPT Sol (gpt-5.6-sol-1)"
            );
        }
    }
}

async function manejarEnvioChatIA(event) {
    if (event) event.preventDefault();
    const input = document.getElementById('ai-chat-input');
    if (!input) return;
    
    const texto = input.value.trim();
    if (!texto) return;
    
    input.value = '';
    await ejecutarConsultaIA(texto);
}

function usarChipIA(textoPrompt) {
    ejecutarConsultaIA(textoPrompt);
}

async function ejecutarConsultaIA(texto) {
    const chatBody = document.getElementById('ai-chat-body');
    if (!chatBody) return;

    // 1. Mostrar mensaje del usuario
    agregarBurbujaUsuario(texto);

    // 2. Mostrar indicador de escritura con identificación del modelo
    const typingId = 'typing-' + Date.now();
    const typingEl = document.createElement('div');
    typingEl.className = 'ai-message bot';
    typingEl.id = typingId;
    typingEl.innerHTML = `
        <div class="ai-bubble" style="border-color: rgba(0, 255, 159, 0.3);">
            <div style="display: flex; align-items: center; gap: 8px; font-size: 0.73rem; color: #00ff9f; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px;">
                <span style="display: inline-block; width: 6px; height: 6px; background: #00ff9f; border-radius: 50%; box-shadow: 0 0 6px #00ff9f;"></span>
                <span>ChatGPT Sol está escribiendo...</span>
            </div>
            <div class="ai-typing-indicator">
                <div class="ai-dot" style="background: #00ff9f;"></div>
                <div class="ai-dot" style="background: #00ff9f;"></div>
                <div class="ai-dot" style="background: #00ff9f;"></div>
            </div>
        </div>
    `;
    chatBody.appendChild(typingEl);
    chatBody.scrollTop = chatBody.scrollHeight;

    // 3. Petición a la API
    try {
        const res = await fetch(`${API_BASE_URL}/api/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mensaje: texto,
                historial: historialChatIA.slice(-6)
            })
        });

        // Eliminar indicador
        const indicador = document.getElementById(typingId);
        if (indicador) indicador.remove();

        if (res.ok) {
            const data = await res.json();
            historialChatIA.push({ role: 'user', content: texto });
            historialChatIA.push({ role: 'assistant', content: data.respuesta });

            const motorUsado = data.motor || "ChatGPT Sol (gpt-5.6-sol-1)";
            
            // Actualizar etiqueta del motor en la barra superior del chat
            const labelEngine = document.getElementById('ai-active-engine-label');
            if (labelEngine) labelEngine.innerText = motorUsado;

            agregarBurbujaBot(data.respuesta, data.prendas_recomendadas || [], motorUsado);

            // Notificación visual Toast en pantalla
            mostrarToast('success', `⚡ Respuesta generada por <b>${escaparHTML(motorUsado)}</b> (Microsoft Foundry)`);


            // Auto-rellenar cupón si el asistente sugiere uno
            if (data.cupon_sugerido && !cuponActivo) {
                const cupInput = document.getElementById('coupon-code');
                if (cupInput) cupInput.value = data.cupon_sugerido;
            }
        } else {
            throw new Error("Respuesta no OK");
        }
    } catch (e) {
        const indicador = document.getElementById(typingId);
        if (indicador) indicador.remove();

        agregarBurbujaBot(
            "⚡ **¡Look Techwear Recomendado!**\n\n" +
            "Para un estilo urbano y nocturno de alto impacto, te sugiero combinar nuestro **Hoodie Cyberpunk Oversize** con el **Pantalón Cargo Tactical**.\n\n" +
            "🎟️ ¡Usa el cupón `NEON10` para un 10% de descuento adicional!",
            [
                {
                    nombre: "Hoodie Cyberpunk Oversize",
                    sku: "HOOD-CYBER-M",
                    precio: 65.00,
                    imagen_url: "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800"
                },
                {
                    nombre: "Pantalón Cargo Tactical 2.0",
                    sku: "PANT-CARG-S",
                    precio: 75.00,
                    imagen_url: "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800"
                }
            ],
            "Motor Local de Respaldo"
        );
        mostrarToast('warning', '⚠️ Consulta procesada por el motor de respaldo local.');
    }
}

function agregarBurbujaUsuario(texto) {
    const chatBody = document.getElementById('ai-chat-body');
    if (!chatBody) return;

    const msg = document.createElement('div');
    msg.className = 'ai-message user';
    msg.innerHTML = `<div class="ai-bubble">${escaparHTML(texto)}</div>`;
    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function agregarBurbujaBot(textoMarkdown, prendas = [], motor = "ChatGPT Sol (gpt-5.6-sol-1)") {
    const chatBody = document.getElementById('ai-chat-body');
    if (!chatBody) return;

    const msg = document.createElement('div');
    msg.className = 'ai-message bot';

    // Parseo simple de markdown a HTML
    let htmlFormateado = textoMarkdown
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
        .replace(/\*(.*?)\*/g, '<i>$1</i>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');

    let cardsHtml = '';
    if (prendas && prendas.length > 0) {
        cardsHtml += '<div class="ai-recommendations-row">';
        prendas.forEach(p => {
            const img = p.imagen_url || 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800';
            cardsHtml += `
                <div class="ai-card-item">
                    <img src="${img}" alt="${p.nombre}" class="ai-card-img" onerror="this.src='https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800'">
                    <div class="ai-card-details">
                        <div class="ai-card-title" title="${p.nombre}">${p.nombre}</div>
                        <div class="ai-card-price">$${p.precio.toFixed(2)} USD</div>
                    </div>
                    <button class="btn-ai-add-cart" onclick="agregarAlCarrito('${p.sku}', ${p.precio})">
                        + Agregar
                    </button>
                </div>
            `;
        });
        cardsHtml += '</div>';
    }

    const badgeColor = motor.includes('ChatGPT Sol') ? '#00ff9f' : 'var(--neon-cyan)';
    const badgeMotor = `
        <div style="display: inline-flex; align-items: center; gap: 7px; font-size: 0.72rem; color: ${badgeColor}; background: rgba(0, 255, 159, 0.08); border: 1px solid rgba(0, 255, 159, 0.25); padding: 4px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace; margin-bottom: 8px; box-shadow: 0 0 10px rgba(0, 255, 159, 0.15);">
            <span style="display: inline-block; width: 7px; height: 7px; background: ${badgeColor}; border-radius: 50%; box-shadow: 0 0 8px ${badgeColor};"></span>
            <span>⚡ <b>${escaparHTML(motor)}</b></span>
        </div>
    `;

    msg.innerHTML = `
        <div class="ai-bubble">
            ${badgeMotor}
            <div style="line-height: 1.55;">${htmlFormateado}</div>
            ${cardsHtml}
        </div>
    `;

    chatBody.appendChild(msg);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function mostrarToast(tipo, mensaje) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast-item ${tipo}`;
    const icon = tipo === 'success' ? '🤖' : (tipo === 'warning' ? '⚠️' : '⚡');
    toast.innerHTML = `<span style="font-size: 1.15rem;">${icon}</span> <span style="font-size: 0.85rem;">${mensaje}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-20px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 300);
        }
    }, 4500);
}

function escaparHTML(str) {
    return String(str).replace(/[&<>'"]/g, tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[tag] || tag));
}

// Inicialización
window.addEventListener('DOMContentLoaded', cargarCatalogo);

