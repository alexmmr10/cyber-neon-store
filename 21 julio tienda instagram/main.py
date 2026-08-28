import os
import sys
import uuid
import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

# Configurar salida estándar para UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI, HTTPException, Query, Path as FastPath, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import httpx
import json
import asyncpg

# Cargar variables de entorno desde .env si existe
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

# Configuración
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5433/tiendadb")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/nueva_orden")
N8N_ESTADO_WEBHOOK_URL = os.getenv("N8N_ESTADO_WEBHOOK_URL", "http://localhost:5678/webhook/cambio_estado_orden")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "cyberneon_secret_2026")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Azure AI Foundry / Microsoft Foundry / ChatGPT Sol
AZURE_AI_ENDPOINT = os.getenv("AZURE_AI_ENDPOINT", "").strip()
AZURE_AI_KEY = os.getenv("AZURE_AI_KEY", "").strip()
AZURE_AI_MODEL = os.getenv("AZURE_AI_MODEL", "gpt-5.6-sol-1").strip()

# Catálogo de Respaldo / Fallback si PostgreSQL no está disponible
CATALOGO_FALLBACK = [
    {
        "nombre": "Hoodie Cyberpunk Oversize",
        "descripcion": "Sudadera pesada de algodón premium 450 GSM con capucha holgada y detalles reflectivos neón magenta en mangas y espalda. Acabado impermeable suave.",
        "categoria": "HOODIES",
        "imagen_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
        "sku": "HOOD-CYBER-M",
        "talla": "M",
        "color": "Negro/Rosa Neón",
        "precio": 65.00,
        "stock": 25
    },
    {
        "nombre": "Camiseta Neon Tech UV",
        "descripcion": "Camiseta de algodón peinado de alta densidad con serigrafía fosforescente reactiva a luz ultravioleta. Corte relaxed fit con cuello reforzado.",
        "categoria": "CAMISETAS",
        "imagen_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80",
        "sku": "TRET-TECH-L",
        "talla": "L",
        "color": "Negro/Morado",
        "precio": 30.00,
        "stock": 30
    },
    {
        "nombre": "Pantalón Cargo Tactical 2.0",
        "descripcion": "Pantalón urbano multibolsillos con correas tácticas ajustables, broches magnéticos y tela ripstop resistente a desgarros.",
        "categoria": "PANTALONES",
        "imagen_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
        "sku": "PANT-CARG-S",
        "talla": "S",
        "color": "Negro Mate",
        "precio": 75.00,
        "stock": 18
    },
    {
        "nombre": "Vestido Neón Noche Cyber",
        "descripcion": "Vestido entallado de diseño futurista con líneas de vivo fluorescente y tela elástica modeladora con acabado satinado oscuro.",
        "categoria": "VESTIDOS",
        "imagen_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80",
        "sku": "VEST-NEON-M",
        "talla": "M",
        "color": "Negro/Morado",
        "precio": 45.00,
        "stock": 25
    },
    {
        "nombre": "Chaqueta Reflejante Matrix",
        "descripcion": "Chaqueta rompevientos con recubrimiento reflectivo tornasol de alta visibilidad nocturna. Cierres impermeables YKK y forro térmico transpirable.",
        "categoria": "HOODIES",
        "imagen_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80",
        "sku": "CHAK-MAT-XL",
        "talla": "XL",
        "color": "Gris Tornasol",
        "precio": 95.00,
        "stock": 15
    },
    {
        "nombre": "Jogger Urbano Future Tech",
        "descripcion": "Pantalón deportivo ajustado de felpa densa con paneles laterales en verde neón, bolsillos con cremallera termosellada y cordón con topes metálicos.",
        "categoria": "PANTALONES",
        "imagen_url": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80",
        "sku": "JOGG-FUT-M",
        "talla": "M",
        "color": "Negro/Verde Neón",
        "precio": 50.00,
        "stock": 30
    },
    {
        "nombre": "Top Deportivo Compresión Cyber",
        "descripcion": "Top elástico de compresión con diseño ergonómico de soporte medio y líneas geométricas reflectantes. Tejido transpirable de secado ultra rápido.",
        "categoria": "CAMISETAS",
        "imagen_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&auto=format&fit=crop&q=80",
        "sku": "TOP-CYB-S",
        "talla": "S",
        "color": "Negro/Rosa Neón",
        "precio": 25.00,
        "stock": 25
    },
    {
        "nombre": "Gorra Snapback DarkNet 3D",
        "descripcion": "Gorra snapback de visera plana con bordado 3D de alta densidad frontal, pin metálico lateral y cierre ajustable de alta resistencia.",
        "categoria": "ACCESORIOS",
        "imagen_url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=800&auto=format&fit=crop&q=80",
        "sku": "GORR-NET-U",
        "talla": "Única",
        "color": "Negro Total / Cyan",
        "precio": 20.00,
        "stock": 40
    }
]

# ==========================================
# GESTIÓN DEL CICLO DE VIDA (LIFESPAN & POOL)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 [FastAPI] Inicializando servidor Tienda Neón...")
    app.state.db_pool = None
    try:
        print(f"📡 Intentando conectar Pool de Conexiones a PostgreSQL ({DATABASE_URL})...")
        ssl_mode = 'require' if ('azure.com' in DATABASE_URL or 'sslmode=require' in DATABASE_URL) else None
        app.state.db_pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            ssl=ssl_mode,
            min_size=2,
            max_size=10,
            command_timeout=15.0,
            timeout=8.0
        )
        print("✅ [FastAPI] Pool de conexiones a PostgreSQL inicializado con éxito.")
    except Exception as e:
        print(f"⚠️  [FastAPI] Nota: No se pudo conectar a PostgreSQL ({e}).")
        print("💡 El servidor operará en modo resiliente (catálogo demo y respuestas simuladas).")
        app.state.db_pool = None

    yield

    # Limpieza al apagar el servidor
    if app.state.db_pool is not None:
        print("🛑 [FastAPI] Cerrando pool de conexiones PostgreSQL...")
        await app.state.db_pool.close()
        print("✅ [FastAPI] Conexiones cerradas.")

app = FastAPI(
    title="⚡ API Tienda Cyber Neón",
    description="Backend oficial de alto rendimiento para e-commerce con PostgreSQL, FastAPI y automatización n8n",
    version="2.0.0",
    lifespan=lifespan
)

# Inicializar estado seguro por defecto
app.state.db_pool = None

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para forzar no-cache en navegador durante desarrollo
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Servir Frontend Estático
BASE_DIR = Path(__file__).parent
if (BASE_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(BASE_DIR / "css")), name="css")
if (BASE_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(BASE_DIR / "js")), name="js")

@app.get("/", summary="Página Principal de la Tienda", include_in_schema=False)
async def serve_index():
    index_file = BASE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    return {"message": "Cyber Neón Store API v2.0 en ejecución"}

@app.get("/index.html", include_in_schema=False)
async def serve_index_html():
    return await serve_index()

@app.get("/admin", summary="Panel Administrativo", include_in_schema=False)
async def serve_admin():
    admin_file = BASE_DIR / "admin.html"
    if admin_file.exists():
        return FileResponse(str(admin_file), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    return {"message": "Panel Admin no encontrado"}

@app.get("/admin.html", include_in_schema=False)
async def serve_admin_html():
    return await serve_admin()





# ==========================================
# MODELOS PYDANTIC V2 (ESQUEMAS DE DATOS)
# ==========================================
class ItemOrden(BaseModel):
    sku: str = Field(..., description="Código único de la variante")
    cantidad: int = Field(..., ge=1, description="Cantidad solicitada")
    precio_unitario: float = Field(..., ge=0.0, description="Precio unitario")
    nombre: Optional[str] = Field(None, description="Nombre de la prenda")
    talla: Optional[str] = Field(None, description="Talla")
    color: Optional[str] = Field(None, description="Color")

class CheckoutOrderRequest(BaseModel):
    telefono_cliente: str = Field(..., min_length=7, max_length=25, description="Número telefónico de WhatsApp")
    pais: str = Field("593", description="Prefijo o código de país")
    total_usd: float = Field(..., ge=0.0, description="Total facturado en USD")
    subtotal_usd: Optional[float] = Field(None, description="Subtotal antes de descuentos y envíos")
    descuento_usd: Optional[float] = Field(0.0, ge=0.0, description="Monto de descuento aplicado")
    envio_usd: Optional[float] = Field(0.0, ge=0.0, description="Costo de envío")
    cupon_codigo: Optional[str] = Field(None, description="Código de cupón utilizado")
    metodo_pago: Optional[str] = Field("WhatsApp / Contraentrega", description="Método de pago seleccionado")
    items: List[ItemOrden] = Field(..., min_length=1, description="Lista de artículos en la orden")

class ProductoCreateRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    descripcion: Optional[str] = Field("", max_length=1000)
    categoria: str = Field("GENERAL", max_length=50)
    imagen_url: Optional[str] = Field(None, max_length=1000)
    sku: str = Field(..., min_length=2, max_length=50)
    talla: str = Field(..., max_length=20)
    color: str = Field(..., max_length=40)
    precio: float = Field(..., ge=0.01)
    stock: int = Field(..., ge=0)

class ProductoUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    imagen_url: Optional[str] = None
    talla: Optional[str] = None
    color: Optional[str] = None
    precio: Optional[float] = Field(None, ge=0.01)
    stock: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

class EstadoOrdenUpdateRequest(BaseModel):
    estado: str = Field(..., description="Nuevo estado: PENDIENTE, PAGADO, PREPARANDO, ENVIADO, ENTREGADO, CANCELADO")
    guia_envio: Optional[str] = Field(None, description="Número o enlace de guía de paquetería")
    notas: Optional[str] = Field(None, description="Notas internas sobre la orden")
    notificar_cliente: Optional[bool] = Field(True, description="Enviar evento a n8n para WhatsApp")

class CuponCreateRequest(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=30)
    tipo: str = Field(..., description="porcentaje, fijo, envio")
    valor: float = Field(..., ge=0.0)
    descripcion: Optional[str] = ""
    minimo_compra: Optional[float] = 0.0

class AIChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000, description="Consulta del cliente sobre estilo, outfits o catálogo")
    historial: Optional[List[Dict[str, str]]] = Field(default=[], description="Historial de mensajes previos")



# ==========================================
# 1. ENDPOINT DE SALUD (HEALTH CHECK)
# ==========================================
@app.get("/api/health", summary="Estado del Servidor y Base de Datos")
async def health_check():
    pool = app.state.db_pool
    db_status = "connected" if pool is not None else "disconnected"
    pool_info = {}

    if pool is not None:
        try:
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            pool_info = {
                "size": pool.get_size(),
                "free": pool.get_idle_size(),
                "max_size": pool.get_max_size()
            }
        except Exception as e:
            db_status = f"error: {e}"

    return {
        "status": "online",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "database": {
            "status": db_status,
            "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
            "pool": pool_info
        },
        "version": "2.0.0"
    }


# ==========================================
# 2. ENDPOINT PARA EL CATÁLOGO (TIENDA)
# ==========================================
@app.get("/api/productos", summary="Listar catálogo de productos y variantes")
async def obtener_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría (HOODIES, CAMISETAS, etc.)"),
    solo_stock: bool = Query(True, description="Mostrar únicamente productos con stock > 0")
):
    pool = app.state.db_pool
    if pool is None:
        # Fallback resiliente si PostgreSQL no está conectado
        resultado = CATALOGO_FALLBACK
        if categoria and categoria.upper() != "TODOS":
            resultado = [p for p in resultado if p["categoria"].upper() == categoria.upper()]
        return resultado

    try:
        async with pool.acquire() as conn:
            query = """
                SELECT 
                    p.id as producto_id,
                    p.nombre, 
                    p.descripcion, 
                    p.categoria,
                    p.imagen_url as producto_imagen,
                    v.id as variante_id,
                    v.sku, 
                    v.talla, 
                    v.color, 
                    v.precio, 
                    v.stock,
                    COALESCE(v.imagen_url, p.imagen_url) as variante_imagen,
                    p.activo
                FROM productos p
                JOIN variantes v ON p.id = v.producto_id
                WHERE p.activo = TRUE
            """
            params = []
            if solo_stock:
                query += " AND v.stock > 0"
            if categoria and categoria.upper() != "TODOS":
                params.append(categoria.upper())
                query += f" AND UPPER(p.categoria) = ${len(params)}"

            query += " ORDER BY p.id ASC, v.id ASC"

            rows = await conn.fetch(query, *params)

            # Agrupar variantes bajo cada producto
            prods_dict = {}
            for row in rows:
                p_id = row["producto_id"]
                if p_id not in prods_dict:
                    prods_dict[p_id] = {
                        "id": p_id,
                        "nombre": row["nombre"],
                        "descripcion": row["descripcion"] or "",
                        "categoria": row["categoria"] or "GENERAL",
                        "imagen_url": row["producto_imagen"] or "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800",
                        "variantes": []
                    }
                prods_dict[p_id]["variantes"].append({
                    "id": row["variante_id"],
                    "sku": row["sku"],
                    "talla": row["talla"],
                    "color": row["color"],
                    "precio": float(row["precio"]),
                    "stock": row["stock"],
                    "imagen_url": row["variante_imagen"] or row["producto_imagen"]
                })

            productos = []
            for p in prods_dict.values():
                vars_list = p["variantes"]
                primera = vars_list[0] if vars_list else {}
                stock_total = sum(v["stock"] for v in vars_list)
                tallas = [v["talla"] for v in vars_list]
                precios = [v["precio"] for v in vars_list]
                
                productos.append({
                    "id": p["id"],
                    "nombre": p["nombre"],
                    "descripcion": p["descripcion"],
                    "categoria": p["categoria"],
                    "imagen_url": p["imagen_url"],
                    "sku": primera.get("sku", ""),
                    "talla": primera.get("talla", ""),
                    "color": primera.get("color", ""),
                    "precio": min(precios) if precios else 0.0,
                    "precio_max": max(precios) if precios else 0.0,
                    "stock": stock_total,
                    "tallas_disponibles": tallas,
                    "variantes": vars_list
                })

            return productos
    except Exception as e:
        print(f"❌ [GET /api/productos] Error al consultar base de datos: {e}")
        # En caso de error inesperado, fallback seguro
        return CATALOGO_FALLBACK


# ==========================================
# 3. ENDPOINT PARA PROCESAR COMPRA (CHECKOUT)
# ==========================================
@app.post("/api/orders/checkout", summary="Procesar compra, descontar stock y despachar webhook")
async def procesar_compra(order_data: CheckoutOrderRequest):
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    print(f"\n🛒 [POST /api/orders/checkout] Procesando {order_id} para {order_data.telefono_cliente}...")

    pool = app.state.db_pool
    items_despacho = [item.model_dump() for item in order_data.items]
    subtotal = order_data.subtotal_usd if order_data.subtotal_usd is not None else sum(i.cantidad * i.precio_unitario for i in order_data.items)

    if pool is not None:
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 1. Verificar stock disponible para cada ítem
                    for item in order_data.items:
                        stock_actual = await conn.fetchval("SELECT stock FROM variantes WHERE sku = $1", item.sku)
                        if stock_actual is None:
                            raise HTTPException(status_code=404, detail=f"El producto con SKU '{item.sku}' no existe en el catálogo.")
                        if stock_actual < item.cantidad:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Stock insuficiente para SKU {item.sku}. Disponible: {stock_actual}, Solicitado: {item.cantidad}"
                            )

                    # 2. Insertar orden maestra
                    orden_db_id = await conn.fetchval("""
                        INSERT INTO ordenes (
                            order_id, telefono_cliente, pais, subtotal_usd, descuento_usd, 
                            envio_usd, total_usd, cupon_codigo, metodo_pago, estado
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'PENDIENTE')
                        RETURNING id
                    """, 
                        order_id, 
                        order_data.telefono_cliente, 
                        order_data.pais, 
                        subtotal,
                        order_data.descuento_usd,
                        order_data.envio_usd,
                        order_data.total_usd,
                        order_data.cupon_codigo,
                        order_data.metodo_pago
                    )

                    # 3. Insertar orden_items y descontar stock en variantes
                    for item in order_data.items:
                        await conn.execute("""
                            INSERT INTO orden_items (orden_id, sku, nombre, talla, color, cantidad, precio_unitario, subtotal)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """, 
                            orden_db_id, 
                            item.sku, 
                            item.nombre or item.sku, 
                            item.talla or "-", 
                            item.color or "-", 
                            item.cantidad, 
                            item.precio_unitario,
                            (item.cantidad * item.precio_unitario)
                        )

                        await conn.execute("""
                            UPDATE variantes
                            SET stock = stock - $1
                            WHERE sku = $2
                        """, item.cantidad, item.sku)

            print(f"✅ [BD] Orden {order_id} persistida y stock descontado con éxito.")
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Error durante la transacción de BD: {e}")
            raise HTTPException(status_code=500, detail=f"Error al guardar la orden: {e}")
    else:
        print(f"⚠️ [Offline Mode] Orden {order_id} procesada en memoria (PostgreSQL desconectado).")

    # 4. Despachar evento a n8n para WhatsApp (Meta Cloud API)
    n8n_payload = {
        "event": "nueva_orden",
        "order_id": order_id,
        "telefono_cliente": order_data.telefono_cliente,
        "pais": order_data.pais,
        "subtotal_usd": subtotal,
        "descuento_usd": order_data.descuento_usd,
        "envio_usd": order_data.envio_usd,
        "total_usd": order_data.total_usd,
        "cupon_codigo": order_data.cupon_codigo,
        "metodo_pago": order_data.metodo_pago,
        "items": items_despacho,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    n8n_enviado = False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(N8N_WEBHOOK_URL, json=n8n_payload, timeout=4.0)
            n8n_enviado = (resp.status_code == 200)
            print(f"📤 Webhook n8n respondió con código: {resp.status_code}")
    except Exception as e:
        print(f"⚠️  No se pudo contactar al webhook n8n ({N8N_WEBHOOK_URL}): {e}")

    return {
        "status": "success",
        "order_id": order_id,
        "telefono": order_data.telefono_cliente,
        "subtotal_usd": subtotal,
        "descuento_usd": order_data.descuento_usd,
        "envio_usd": order_data.envio_usd,
        "total_usd": order_data.total_usd,
        "items": items_despacho,
        "n8n_notificado": n8n_enviado,
        "message": "Orden procesada exitosamente y ticket generado."
    }


# ==========================================
# 4. ENDPOINTS PARA EL PANEL DE ADMINISTRACIÓN
# ==========================================
@app.get("/api/admin/ventas", summary="Estadísticas globales de ventas y pedidos")
async def obtener_estadisticas_ventas():
    pool = app.state.db_pool
    if pool is None:
        # Fallback de demostración
        return {
            "total_ventas": 12,
            "recaudacion_total": 740.00,
            "compra_mas_cara": 190.00,
            "ordenes_pendientes": 3,
            "ticket_promedio": 61.67,
            "historial": [
                {"order_id": "ORD-984210", "telefono": "+593991234567", "total_usd": 190.00, "estado": "PAGADO", "fecha": "2026-08-24 14:15"},
                {"order_id": "ORD-773120", "telefono": "+593987654321", "total_usd": 95.00, "estado": "ENVIADO", "fecha": "2026-08-24 13:40"},
                {"order_id": "ORD-441299", "telefono": "+593992345678", "total_usd": 65.00, "estado": "PENDIENTE", "fecha": "2026-08-24 12:10"},
            ]
        }

    try:
        async with pool.acquire() as conn:
            total_ordenes = await conn.fetchval("SELECT COUNT(*) FROM ordenes")
            recaudacion = await conn.fetchval("SELECT COALESCE(SUM(total_usd), 0) FROM ordenes")
            compra_max = await conn.fetchval("SELECT COALESCE(MAX(total_usd), 0) FROM ordenes")
            pendientes = await conn.fetchval("SELECT COUNT(*) FROM ordenes WHERE estado = 'PENDIENTE'")

            ticket_promedio = (float(recaudacion) / total_ordenes) if total_ordenes > 0 else 0.0

            historial = await conn.fetch("""
                SELECT order_id, telefono_cliente as telefono, total_usd, estado, fecha_creacion as fecha
                FROM ordenes
                ORDER BY fecha_creacion DESC
                LIMIT 50
            """)

            return {
                "total_ventas": total_ordenes,
                "recaudacion_total": float(recaudacion),
                "compra_mas_cara": float(compra_max),
                "ordenes_pendientes": pendientes,
                "ticket_promedio": round(ticket_promedio, 2),
                "historial": [
                    {
                        "order_id": row["order_id"],
                        "telefono": row["telefono"],
                        "total_usd": float(row["total_usd"]),
                        "estado": row["estado"] or "PENDIENTE",
                        "fecha": row["fecha"].strftime("%Y-%m-%d %H:%M") if row["fecha"] else "N/A"
                    }
                    for row in historial
                ]
            }
    except Exception as e:
        print(f"❌ Error al consultar estadísticas de admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/ordenes/{order_id}", summary="Detalle completo de una orden específica")
async def obtener_detalle_orden(order_id: str = FastPath(..., description="ID único de orden")):
    pool = app.state.db_pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible.")

    async with pool.acquire() as conn:
        orden = await conn.fetchrow("""
            SELECT id, order_id, telefono_cliente, pais, subtotal_usd, descuento_usd, 
                   envio_usd, total_usd, cupon_codigo, metodo_pago, estado, guia_envio, notas, fecha_creacion
            FROM ordenes
            WHERE order_id = $1
        """, order_id)

        if not orden:
            raise HTTPException(status_code=404, detail=f"La orden '{order_id}' no fue encontrada.")

        items = await conn.fetch("""
            SELECT sku, nombre, talla, color, cantidad, precio_unitario, subtotal
            FROM orden_items
            WHERE orden_id = $1
        """, orden["id"])

        return {
            "order_id": orden["order_id"],
            "telefono": orden["telefono_cliente"],
            "pais": orden["pais"],
            "subtotal_usd": float(orden["subtotal_usd"]),
            "descuento_usd": float(orden["descuento_usd"]),
            "envio_usd": float(orden["envio_usd"]),
            "total_usd": float(orden["total_usd"]),
            "cupon_codigo": orden["cupon_codigo"],
            "metodo_pago": orden["metodo_pago"],
            "estado": orden["estado"],
            "guia_envio": orden["guia_envio"],
            "notas": orden["notas"],
            "fecha": orden["fecha_creacion"].strftime("%Y-%m-%d %H:%M:%S") if orden["fecha_creacion"] else "N/A",
            "items": [
                {
                    "sku": i["sku"],
                    "nombre": i["nombre"],
                    "talla": i["talla"],
                    "color": i["color"],
                    "cantidad": i["cantidad"],
                    "precio_unitario": float(i["precio_unitario"]),
                    "subtotal": float(i["subtotal"])
                }
                for i in items
            ]
        }


@app.patch("/api/admin/ordenes/{order_id}/estado", summary="Actualizar estado de una orden")
async def actualizar_estado_orden(order_id: str, data: EstadoOrdenUpdateRequest):
    pool = app.state.db_pool
    if pool is None:
        return {"status": "success", "order_id": order_id, "nuevo_estado": data.estado, "mode": "demo"}

    async with pool.acquire() as conn:
        orden = await conn.fetchrow("SELECT id, telefono_cliente, total_usd FROM ordenes WHERE order_id = $1", order_id)
        if not orden:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        await conn.execute("""
            UPDATE ordenes
            SET estado = $1, guia_envio = COALESCE($2, guia_envio), notas = COALESCE($3, notas), fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE order_id = $4
        """, data.estado.upper(), data.guia_envio, data.notas, order_id)

    # Notificar a n8n para WhatsApp si se solicita
    if data.notificar_cliente:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(N8N_ESTADO_WEBHOOK_URL, json={
                    "event": "cambio_estado_orden",
                    "order_id": order_id,
                    "telefono": orden["telefono_cliente"],
                    "nuevo_estado": data.estado.upper(),
                    "guia_envio": data.guia_envio,
                    "notas": data.notas
                }, timeout=3.0)
        except Exception as e:
            print(f"⚠️ Nota: No se pudo enviar webhook de estado a n8n: {e}")

    return {"status": "success", "order_id": order_id, "nuevo_estado": data.estado.upper()}


@app.post("/api/admin/productos", summary="Registrar nuevo producto y variante")
async def crear_nuevo_producto(data: ProductoCreateRequest):
    pool = app.state.db_pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible para inserciones.")

    async with pool.acquire() as conn:
        async with conn.transaction():
            existe = await conn.fetchval("SELECT 1 FROM variantes WHERE sku = $1", data.sku)
            if existe:
                raise HTTPException(status_code=400, detail=f"El SKU '{data.sku}' ya está registrado.")

            prod_id = await conn.fetchval("""
                INSERT INTO productos (nombre, descripcion, categoria, imagen_url, activo)
                VALUES ($1, $2, $3, $4, TRUE) 
                RETURNING id
            """, data.nombre, data.descripcion, data.categoria.upper(), data.imagen_url)

            await conn.execute("""
                INSERT INTO variantes (producto_id, sku, talla, color, precio, stock, imagen_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, prod_id, data.sku, data.talla, data.color, data.precio, data.stock, data.imagen_url)

    return {"status": "success", "message": f"Producto '{data.nombre}' registrado con SKU {data.sku}"}


@app.put("/api/admin/productos/{sku}", summary="Actualizar producto y variante de forma integral")
async def actualizar_producto_sku(sku: str, data: ProductoUpdateRequest):
    pool = app.state.db_pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible.")

    async with pool.acquire() as conn:
        variante = await conn.fetchrow("SELECT id, producto_id FROM variantes WHERE sku = $1", sku)
        if not variante:
            raise HTTPException(status_code=404, detail="Variante no encontrada")

        async with conn.transaction():
            # 1. Actualizar datos específicos de la variante
            if data.precio is not None or data.stock is not None or data.imagen_url is not None or data.talla is not None or data.color is not None:
                await conn.execute("""
                    UPDATE variantes
                    SET precio = COALESCE($1, precio),
                        stock = COALESCE($2, stock),
                        imagen_url = COALESCE($3, imagen_url),
                        talla = COALESCE($4, talla),
                        color = COALESCE($5, color)
                    WHERE sku = $6
                """, data.precio, data.stock, data.imagen_url, data.talla, data.color, sku)

            # 2. Actualizar datos generales del producto padre
            if data.nombre is not None or data.descripcion is not None or data.categoria is not None or data.imagen_url is not None or data.activo is not None:
                cat_val = data.categoria.upper() if data.categoria else None
                await conn.execute("""
                    UPDATE productos
                    SET nombre = COALESCE($1, nombre),
                        descripcion = COALESCE($2, descripcion),
                        categoria = COALESCE($3, categoria),
                        imagen_url = COALESCE($4, imagen_url),
                        activo = COALESCE($5, activo)
                    WHERE id = $6
                """, data.nombre, data.descripcion, cat_val, data.imagen_url, data.activo, variante["producto_id"])

    return {"status": "success", "message": f"Prenda '{sku}' y sus datos de producto actualizados con éxito en Azure PostgreSQL."}


@app.delete("/api/admin/productos/{sku}", summary="Desactivar o eliminar una variante")
async def eliminar_o_desactivar_producto(sku: str, hard_delete: bool = False):
    pool = app.state.db_pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible.")

    async with pool.acquire() as conn:
        variante = await conn.fetchrow("SELECT id, producto_id FROM variantes WHERE sku = $1", sku)
        if not variante:
            raise HTTPException(status_code=404, detail="Variante no encontrada")

        if hard_delete:
            await conn.execute("DELETE FROM productos WHERE id = $1", variante["producto_id"])
            return {"status": "success", "message": f"Producto y variante {sku} eliminados permanentemente."}
        else:
            await conn.execute("UPDATE productos SET activo = FALSE WHERE id = $1", variante["producto_id"])
            return {"status": "success", "message": f"Producto con SKU {sku} desactivado de la tienda."}


# ==========================================
# 5. GESTIÓN DE CUPONES DE DESCUENTO
# ==========================================
@app.get("/api/cupones/{codigo}", summary="Validar cupón de descuento")
async def validar_cupon(codigo: str):
    codigo_clean = codigo.strip().upper()
    pool = app.state.db_pool

    # Validación fallback en caso de no haber DB
    if pool is None:
        cupones_demo = {
            "NEON10": {"codigo": "NEON10", "tipo": "porcentaje", "valor": 0.10, "descripcion": "10% de Descuento", "minimo": 0.0},
            "CYBER20": {"codigo": "CYBER20", "tipo": "porcentaje", "valor": 0.20, "descripcion": "20% Cyber VIP", "minimo": 50.0},
            "ENVIOGRATIS": {"codigo": "ENVIOGRATIS", "tipo": "envio", "valor": 5.00, "descripcion": "Envío Gratis", "minimo": 30.0}
        }
        if codigo_clean in cupones_demo:
            return {"valido": True, **cupones_demo[codigo_clean]}
        raise HTTPException(status_code=404, detail="Cupón inválido o no existente.")

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT codigo, tipo, valor, descripcion, minimo_compra, activo
            FROM cupones
            WHERE codigo = $1 AND activo = TRUE
        """, codigo_clean)

        if not row:
            raise HTTPException(status_code=404, detail="Cupón no válido o caducado.")

        return {
            "valido": True,
            "codigo": row["codigo"],
            "tipo": row["tipo"],
            "valor": float(row["valor"]),
            "descripcion": row["descripcion"],
            "minimo": float(row["minimo_compra"])
        }


# ==========================================
# 6. ASISTENTE IA DE ESTILO NEÓN & AUTOMATIZACIONES
# ==========================================
async def _obtener_catalogo_para_ia() -> List[Dict[str, Any]]:
    pool = app.state.db_pool
    if pool is None:
        return CATALOGO_FALLBACK

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    p.nombre, 
                    p.descripcion, 
                    p.categoria,
                    COALESCE(v.imagen_url, p.imagen_url) as imagen_url,
                    v.sku, 
                    v.talla, 
                    v.color, 
                    v.precio, 
                    v.stock
                FROM productos p
                JOIN variantes v ON p.id = v.producto_id
                WHERE p.activo = TRUE AND v.stock > 0
                ORDER BY p.id ASC
            """)
            return [
                {
                    "nombre": r["nombre"],
                    "descripcion": r["descripcion"] or "",
                    "categoria": r["categoria"] or "GENERAL",
                    "imagen_url": r["imagen_url"] or "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800",
                    "sku": r["sku"],
                    "talla": r["talla"],
                    "color": r["color"],
                    "precio": float(r["precio"]),
                    "stock": r["stock"]
                }
                for r in rows
            ]
    except Exception as e:
        print(f"⚠️ Error al obtener catálogo para IA: {e}")
        return CATALOGO_FALLBACK


def _normalizar_endpoint_azure(raw_endpoint: str, model: str) -> str:
    url = raw_endpoint.strip()
    if not url:
        return ""
    if "/chat/completions" in url:
        return url
    
    url_clean = url.rstrip("/")
    if "api/projects" in url_clean:
        return f"{url_clean}/chat/completions?api-version=2024-05-01-preview"
    elif "services.ai.azure.com" in url_clean or "models.ai.azure.com" in url_clean:
        return f"{url_clean}/models/chat/completions?api-version=2024-05-01-preview"
    elif "openai.azure.com" in url_clean:
        return f"{url_clean}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
    else:
        return f"{url_clean}/chat/completions"


@app.post("/api/ai/chat", summary="Asistente IA de Estilo Neón y Recomendación de Outfits")
async def chat_asistente_ia(req: AIChatRequest):
    mensaje_usuario = req.mensaje.strip()
    catalogo = await _obtener_catalogo_para_ia()
    catalogo_resumen = "\n".join([
        f"- SKU: {p['sku']} | Nombre: {p['nombre']} | Cat: {p['categoria']} | Talla: {p['talla']} | Color: {p['color']} | Precio: ${p['precio']:.2f} | Stock: {p['stock']} | Desc: {p['descripcion']}"
        for p in catalogo
    ])

    system_instruction = (
        "Eres 'Cyber Stylist Neón', el asesor de moda de vanguardia, techwear y cyberpunk de la tienda Cyber Neón Store. "
        "Tu misión es aconsejar al cliente con respuestas atractivas, modernas y con estilo. "
        "REGLAS OBLIGATORIAS:\n"
        "1. Recomienda combinaciones de outfits usando EXCLUSIVAMENTE las prendas del catálogo proporcionado.\n"
        "2. Si el cliente pide combinar una prenda, sugiere partes superiores, inferiores o accesorios que hagan juego (ej. Hoodie + Pantalón Cargo + Gorra).\n"
        "3. Si el usuario pregunta por descuentos, menciona los cupones activos: NEON10 (10% de descuento) o CYBER20 (20% en compras mayores a $50).\n"
        "4. Debes responder en formato JSON estricto con las siguientes claves:\n"
        "   - 'respuesta': tu respuesta conversacional en español con emojis y formato markdown.\n"
        "   - 'skus_recomendados': lista de strings con los SKUs exactos de las prendas que recomendaste.\n"
        "   - 'cupon_sugerido': string con el código del cupón si aplica, o null.\n\n"
        f"CATÁLOGO EN VIVO:\n{catalogo_resumen}"
    )

    # -------------------------------------------------------------
    # 1. INTENTAR LLAMADA A AZURE AI FOUNDRY / CHATGPT SOL
    # -------------------------------------------------------------
    if AZURE_AI_ENDPOINT and AZURE_AI_KEY:
        try:
            target_url = _normalizar_endpoint_azure(AZURE_AI_ENDPOINT, AZURE_AI_MODEL)
            headers = {
                "Content-Type": "application/json",
                "api-key": AZURE_AI_KEY,
                "Authorization": f"Bearer {AZURE_AI_KEY}"
            }

            # Compactar historial para no sobrecargar el modelo
            messages = [{"role": "system", "content": system_instruction}]
            for h in (req.historial or [])[-4:]:
                if isinstance(h, dict) and "role" in h and "content" in h:
                    contenido_limpio = str(h["content"])[:350]
                    messages.append({"role": h["role"], "content": contenido_limpio})
            messages.append({"role": "user", "content": mensaje_usuario})

            payload = {
                "messages": messages,
                "model": AZURE_AI_MODEL
            }

            timeout_cfg = httpx.Timeout(35.0, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                res = await client.post(target_url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    texto_ia = data["choices"][0]["message"]["content"].strip()
                    
                    # Limpiar delimitadores markdown si el modelo los incluye (```json ... ```)
                    texto_limpio = texto_ia
                    if texto_limpio.startswith("```json"):
                        texto_limpio = texto_limpio[7:]
                    elif texto_limpio.startswith("```"):
                        texto_limpio = texto_limpio[3:]
                    if texto_limpio.endswith("```"):
                        texto_limpio = texto_limpio[:-3]
                    texto_limpio = texto_limpio.strip()

                    try:
                        parsed = json.loads(texto_limpio)
                    except Exception:
                        parsed = {"respuesta": texto_ia, "skus_recomendados": []}

                    skus_rec = parsed.get("skus_recomendados", [])
                    if not isinstance(skus_rec, list):
                        skus_rec = []
                    
                    # Buscar SKUs válidos del catálogo
                    prendas_objs = [p for p in catalogo if p["sku"] in skus_rec]
                    
                    # Si el modelo mencionó prendas pero no los SKUs exactos, buscar por coincidencia de nombre o categoría
                    if not prendas_objs:
                        for p in catalogo:
                            if p["nombre"].lower() in texto_ia.lower() or p["categoria"].lower() in texto_ia.lower():
                                if p not in prendas_objs:
                                    prendas_objs.append(p)
                                if len(prendas_objs) >= 3:
                                    break

                    # Si aún está vacío, sugerir las 2 prendas estrella del catálogo
                    respuesta_final = ""
                    if isinstance(parsed, dict):
                        respuesta_final = (
                            parsed.get("respuesta") or 
                            parsed.get("response") or 
                            parsed.get("mensaje") or 
                            parsed.get("content") or 
                            parsed.get("answer") or 
                            ""
                        )
                    if not respuesta_final or not str(respuesta_final).strip() or str(respuesta_final).strip() in [".", "..", "...", "null"]:
                        respuesta_final = texto_ia if (texto_ia and texto_ia.strip() not in [".", "null"]) else "⚡ Puedo ayudarte a encontrar combinaciones ideales. Indícame qué tipo de estilo o prenda buscas."

                    print(f"🤖 [ChatGPT Sol] ✅ Respuesta generada exitosamente por {AZURE_AI_MODEL} desde Microsoft Foundry.")

                    return {
                        "motor": f"ChatGPT Sol ({AZURE_AI_MODEL})",
                        "respuesta": respuesta_final,
                        "prendas_recomendadas": prendas_objs[:4],
                        "cupon_sugerido": parsed.get("cupon_sugerido") or "NEON10"
                    }
                else:
                    print(f"⚠️ [ChatGPT Sol] Azure AI respondió con status {res.status_code}: {res.text}")
        except Exception as e:
            print(f"⚠️ [ChatGPT Sol Error] Tipo: {type(e).__name__} | Detalle: {e or repr(e)}. Intentando alternativa...")

    # -------------------------------------------------------------
    # 2. INTENTAR LLAMADA A GOOGLE GEMINI API
    # -------------------------------------------------------------
    if GEMINI_API_KEY:
        try:
            gemini_payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"System: {system_instruction}\n\nConsulta del cliente: {mensaje_usuario}"}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "responseMimeType": "application/json"
                }
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=gemini_payload, timeout=8.0)
                if res.status_code == 200:
                    data = res.json()
                    texto_ia = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(texto_ia)
                    
                    skus_rec = parsed.get("skus_recomendados", [])
                    prendas_objs = [p for p in catalogo if p["sku"] in skus_rec]

                    return {
                        "motor": "gemini-2.5-flash",
                        "respuesta": parsed.get("respuesta", "¡Excelente elección! Aquí tienes las mejores combinaciones."),
                        "prendas_recomendadas": prendas_objs[:4],
                        "cupon_sugerido": parsed.get("cupon_sugerido")
                    }
        except Exception as e:
            print(f"⚠️ Nota: Fallback de Gemini API ({e}). Usando motor heurístico local.")

    # -------------------------------------------------------------
    # 3. MOTOR DE ESTILISMO HEURÍSTICO INTELIGENTE (OFFLINE / FALLBACK)
    # -------------------------------------------------------------
    msg_low = mensaje_usuario.lower()
    skus_sugeridos = []
    cupon = None
    respuesta = ""

    # Caso 1: Preguntas sobre cupones / ofertas / descuentos
    if any(w in msg_low for w in ["cupon", "cupón", "descuento", "promocion", "promoción", "rebaja", "oferta"]):
        cupon = "NEON10"
        respuesta = (
            "⚡ **¡Tenemos promociones activas para ti!**\n\n"
            "• 🎟️ Usa el cupón `NEON10` para un **10% de Descuento** en todo el catálogo.\n"
            "• 💎 Si tu compra supera los $50, aplica `CYBER20` para un **20% OFF**.\n"
            "• 🚚 Además, ¡tienes **Envío Gratis** garantizado en pedidos desde $100 USD!\n\n"
            "¿Te gustaría que te arme un outfit completo para aprovechar el descuento?"
        )
        skus_sugeridos = ["HOOD-CYBER-M", "PANT-CARG-S", "GORR-NET-U"]

    # Caso 2: Combinar Hoodie o Chaqueta
    elif any(w in msg_low for w in ["hoodie", "sudadera", "chaqueta", "jacket", "matrix", "abrig"]):
        cupon = "NEON10"
        respuesta = (
            "🔥 **¡Combinación Techwear Épica!**\n\n"
            "Para un estilo cyberpunk de alto impacto, te recomiendo combinar la prenda superior con nuestro **Pantalón Cargo Tactical** (con correas ajustables) "
            "y rematar el look con la **Gorra Snapback DarkNet 3D** con bordado neón.\n\n"
            "✨ *Look total reflectivo y urbano de noche.*"
        )
        skus_sugeridos = ["HOOD-CYBER-M", "PANT-CARG-S", "GORR-NET-U"]

    # Caso 3: Combinar Camiseta, Top o Vestido
    elif any(w in msg_low for w in ["camiseta", "top", "vestido", "remera", "t-shirt"]):
        respuesta = (
            "💜 **¡Look Urbano & Fresco!**\n\n"
            "Las camisetas y tops con estampados reactivos a UV se ven brutales cuando las contrastas con el **Jogger Urbano Future Tech** en verde neón. "
            "Si buscas un estilo más formal para eventos nocturnos, el **Vestido Neón Noche** entallado es la opción favorita."
        )
        skus_sugeridos = ["TRET-TECH-L", "JOGG-FUT-M", "VEST-NEON-M"]

    # Caso 4: Buscar por presupuesto o prendas baratas
    elif any(w in msg_low for w in ["presupuesto", "barato", "economico", "económico", "menos de", "<", "100", "50", "80"]):
        cupon = "NEON10"
        prendas_economicas = sorted(catalogo, key=lambda x: x["precio"])[:3]
        skus_sugeridos = [p["sku"] for p in prendas_economicas]
        total_combo = sum(p["precio"] for p in prendas_economicas)
        respuesta = (
            f"💰 **¡Combo Imbatible por Menos de $100!**\n\n"
            f"Te seleccioné las 3 prendas con mejor relación calidad/precio de la tienda. Juntas suman solo **${total_combo:.2f} USD** "
            f"y si usas el cupón `NEON10` te queda aún más accesible.\n\n"
            "¡Puedes agregarlas directamente a tu carrito desde aquí!"
        )

    # Caso 5: Outfit para fiesta, noche, rave o festival
    elif any(w in msg_low for w in ["fiesta", "noche", "rave", "festival", "evento", "outfit", "combinar", "combinacion"]):
        cupon = "CYBER20"
        respuesta = (
            "✨ **¡Outfit Cyberpunk Night Ready!**\n\n"
            "Para destacar en la oscuridad con luz ultravioleta, el combo perfecto es:\n"
            "1. **Chaqueta Reflejante Matrix** (acabado tornasol visible a larga distancia)\n"
            "2. **Camiseta Neon Tech UV** (serigrafía fluorescente)\n"
            "3. **Pantalón Cargo Tactical 2.0** con correas magnéticas\n\n"
            "🎟️ Supera los $50, así que aplica el cupón `CYBER20` para ahorrar el 20%."
        )
        skus_sugeridos = ["CHAK-MAT-XL", "TRET-TECH-L", "PANT-CARG-S"]

    # Caso 6: Consulta por Talla
    elif any(w in msg_low for w in ["talla s", "talla m", "talla l", "talla xl"]):
        talla_buscada = "M"
        for t in ["xl", "l", "m", "s", "xs"]:
            if f"talla {t}" in msg_low or f"talla:{t}" in msg_low:
                talla_buscada = t.upper()
                break

        prendas_talla = [p for p in catalogo if p["talla"].upper() == talla_buscada]
        skus_sugeridos = [p["sku"] for p in prendas_talla[:3]]
        respuesta = (
            f"📏 **Prendas disponibles en Talla {talla_buscada}:**\n\n"
            f"Actualmente tenemos {len(prendas_talla)} prendas con stock inmediato en talla **{talla_buscada}**. "
            f"Aquí tienes las más destacadas para tu colección."
        )

    # Caso por Defecto
    else:
        cupon = "NEON10"
        respuesta = (
            "⚡ **¡Hola! Soy tu Asistente de Estilo Neón.**\n\n"
            "Puedo ayudarte a armar combinaciones completas de techwear, sugerirte tallas o armar un outfit a tu medida. "
            "Aquí tienes nuestras prendas más vendidas de la temporada para empezar. ¡Haz clic en '+ Agregar' en la que más te guste!"
        )
        skus_sugeridos = ["HOOD-CYBER-M", "PANT-CARG-S", "CHAK-MAT-XL", "GORR-NET-U"]

    prendas_finales = [p for p in catalogo if p["sku"] in skus_sugeridos]

    return {
        "motor": "heuristico-inteligente",
        "respuesta": respuesta,
        "prendas_recomendadas": prendas_finales,
        "cupon_sugerido": cupon
    }


@app.post("/api/admin/test-webhook", summary="Probar despacho de webhook a n8n")
async def probar_webhook_n8n():
    test_payload = {
        "event": "test_ping",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "message": "Prueba de conectividad desde Cyber Neón Admin Panel"
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(N8N_WEBHOOK_URL, json=test_payload, timeout=3.0)
            return {
                "status": "success",
                "webhook_url": N8N_WEBHOOK_URL,
                "http_status": res.status_code,
                "message": "Webhook contactado exitosamente."
            }
    except Exception as e:
        return {
            "status": "warning",
            "webhook_url": N8N_WEBHOOK_URL,
            "error": str(e),
            "message": "No se pudo conectar con el servidor n8n en la URL configurada."
        }


# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*85)
    print("🚀 SERVIDOR FASTAPI CYBER NEÓN STORE v2.0")
    print("="*85)
    print(f"📍 Servidor: http://{HOST}:{PORT}")
    print(f"📚 Documentación Swagger UI: http://{HOST}:{PORT}/docs")
    print(f"💚 Health check: http://{HOST}:{PORT}/api/health")
    print(f"📡 Base de Datos: {DATABASE_URL}")
    print("="*85 + "\n")
    uvicorn.run(app, host=HOST, port=PORT)