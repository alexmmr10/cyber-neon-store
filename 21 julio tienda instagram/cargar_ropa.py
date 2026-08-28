import asyncio
import os
import sys
from pathlib import Path

# Configurar salida estándar para UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5433/tiendadb")

async def poblar_catalogo_masivo():
    ssl_mode = 'require' if ('azure.com' in DATABASE_URL or 'sslmode=require' in DATABASE_URL) else None
    conn = await asyncpg.connect(DATABASE_URL, ssl=ssl_mode)
    try:
        # 1. Reiniciar tablas
        print("🗑️  Limpiando tablas antiguas...")
        await conn.execute("DROP TABLE IF EXISTS orden_items CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS variantes CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS cupones CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS productos CASCADE;")
        await conn.execute("DROP TABLE IF EXISTS ordenes CASCADE;")

        # 2. Crear tablas con el esquema modernizado
        print("🏗️  Creando tablas con esquema enriquecido...")
        await conn.execute("""
            CREATE TABLE productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL,
                descripcion TEXT,
                categoria VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
                imagen_url TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.execute("""
            CREATE TABLE variantes (
                id SERIAL PRIMARY KEY,
                producto_id INT REFERENCES productos(id) ON DELETE CASCADE,
                sku VARCHAR(50) UNIQUE NOT NULL,
                talla VARCHAR(20) NOT NULL,
                color VARCHAR(40) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                imagen_url TEXT
            );
        """)

        await conn.execute("""
            CREATE TABLE cupones (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(30) UNIQUE NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                descripcion TEXT,
                minimo_compra DECIMAL(10,2) DEFAULT 0.00,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.execute("""
            CREATE TABLE ordenes (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(50) UNIQUE NOT NULL,
                telefono_cliente VARCHAR(30) NOT NULL,
                pais VARCHAR(10) DEFAULT '593',
                subtotal_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                descuento_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                envio_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                total_usd DECIMAL(10,2) NOT NULL,
                cupon_codigo VARCHAR(30),
                metodo_pago VARCHAR(50) DEFAULT 'WhatsApp / Contraentrega',
                estado VARCHAR(30) DEFAULT 'PENDIENTE',
                guia_envio VARCHAR(100),
                notas TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        await conn.execute("""
            CREATE TABLE orden_items (
                id SERIAL PRIMARY KEY,
                orden_id INT REFERENCES ordenes(id) ON DELETE CASCADE,
                sku VARCHAR(50) NOT NULL,
                nombre VARCHAR(120),
                talla VARCHAR(20),
                color VARCHAR(40),
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL
            );
        """)

        # 3. Insertar Catálogo de Ropa Cyberpunk & Techwear
        print("👕 Insertando prendas del catálogo...")
        prendas = [
            {
                "nombre": "Hoodie Cyberpunk Oversize",
                "descripcion": "Sudadera pesada de algodón premium 450 GSM con capucha holgada y detalles reflectivos neón magenta en mangas y espalda. Acabado impermeable suave.",
                "categoria": "HOODIES",
                "imagen_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("HOOD-CYBER-M", "M", "Negro/Rosa Neón", 65.00, 25),
                    ("HOOD-CYBER-L", "L", "Negro/Rosa Neón", 65.00, 30),
                    ("HOOD-CYBER-XL", "XL", "Negro/Rosa Neón", 68.00, 15)
                ]
            },
            {
                "nombre": "Camiseta Neon Tech UV",
                "descripcion": "Camiseta de algodón peinado de alta densidad con serigrafía fosforescente reactiva a luz ultravioleta. Corte relaxed fit con cuello reforzado.",
                "categoria": "CAMISETAS",
                "imagen_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("TRET-TECH-S", "S", "Negro/Morado", 30.00, 20),
                    ("TRET-TECH-M", "M", "Negro/Morado", 30.00, 35),
                    ("TRET-TECH-L", "L", "Negro/Morado", 30.00, 30)
                ]
            },
            {
                "nombre": "Pantalón Cargo Tactical 2.0",
                "descripcion": "Pantalón urbano multibolsillos con correas tácticas ajustables, broches magnéticos y tela ripstop resistente a desgarros.",
                "categoria": "PANTALONES",
                "imagen_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("PANT-CARG-S", "S", "Negro Mate", 75.00, 18),
                    ("PANT-CARG-M", "M", "Negro Mate", 75.00, 28),
                    ("PANT-CARG-L", "L", "Negro Mate", 75.00, 22)
                ]
            },
            {
                "nombre": "Vestido Neón Noche Cyber",
                "descripcion": "Vestido entallado de diseño futurista con líneas de vivo fluorescente y tela elástica modeladora con acabado satinado oscuro.",
                "categoria": "VESTIDOS",
                "imagen_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("VEST-NEON-S", "S", "Negro/Morado", 45.00, 15),
                    ("VEST-NEON-M", "M", "Negro/Morado", 45.00, 25)
                ]
            },
            {
                "nombre": "Chaqueta Reflejante Matrix",
                "descripcion": "Chaqueta rompevientos con recubrimiento reflectivo tornasol de alta visibilidad nocturna. Cierres impermeables YKK y forro térmico transpirable.",
                "categoria": "HOODIES",
                "imagen_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("CHAK-MAT-M", "M", "Gris Tornasol", 95.00, 12),
                    ("CHAK-MAT-L", "L", "Gris Tornasol", 95.00, 20),
                    ("CHAK-MAT-XL", "XL", "Gris Tornasol", 95.00, 15)
                ]
            },
            {
                "nombre": "Jogger Urbano Future Tech",
                "descripcion": "Pantalón deportivo ajustado de felpa densa con paneles laterales en verde neón, bolsillos con cremallera termosellada y cordón con topes metálicos.",
                "categoria": "PANTALONES",
                "imagen_url": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("JOGG-FUT-S", "S", "Negro/Verde Neón", 50.00, 20),
                    ("JOGG-FUT-M", "M", "Negro/Verde Neón", 50.00, 30),
                    ("JOGG-FUT-L", "L", "Negro/Verde Neón", 50.00, 18)
                ]
            },
            {
                "nombre": "Top Deportivo Compresión Cyber",
                "descripcion": "Top elástico de compresión con diseño ergonómico de soporte medio y líneas geométricas reflectantes. Tejido transpirable de secado ultra rápido.",
                "categoria": "CAMISETAS",
                "imagen_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("TOP-CYB-XS", "XS", "Negro/Rosa Neón", 25.00, 15),
                    ("TOP-CYB-S", "S", "Negro/Rosa Neón", 25.00, 25),
                    ("TOP-CYB-M", "M", "Negro/Rosa Neón", 25.00, 20)
                ]
            },
            {
                "nombre": "Gorra Snapback DarkNet 3D",
                "descripcion": "Gorra snapback de visera plana con bordado 3D de alta densidad frontal, pin metálico lateral y cierre ajustable de alta resistencia.",
                "categoria": "ACCESORIOS",
                "imagen_url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=800&auto=format&fit=crop&q=80",
                "variantes": [
                    ("GORR-NET-U", "Única", "Negro Total / Cyan", 20.00, 40)
                ]
            }
        ]

        for p in prendas:
            prod_id = await conn.fetchval("""
                INSERT INTO productos (nombre, descripcion, categoria, imagen_url, activo)
                VALUES ($1, $2, $3, $4, TRUE)
                RETURNING id
            """, p["nombre"], p["descripcion"], p["categoria"], p["imagen_url"])

            for sku, talla, color, precio, stock in p["variantes"]:
                await conn.execute("""
                    INSERT INTO variantes (producto_id, sku, talla, color, precio, stock, imagen_url)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, prod_id, sku, talla, color, precio, stock, p["imagen_url"])

        # 4. Insertar Cupones de Descuento Iniciales
        print("🎟️  Insertando cupones promocionales...")
        cupones = [
            ("NEON10", "porcentaje", 0.10, "10% de Descuento Especial en todo el catálogo", 0.0),
            ("CYBER20", "porcentaje", 0.20, "20% de Descuento VIP Cyberpunk", 50.0),
            ("ENVIOGRATIS", "envio", 5.00, "Envío Gratis Garantizado a todo el país", 30.0)
        ]

        for cod, tipo, val, desc, min_c in cupones:
            await conn.execute("""
                INSERT INTO cupones (codigo, tipo, valor, descripcion, minimo_compra, activo)
                VALUES ($1, $2, $3, $4, $5, TRUE)
            """, cod, tipo, val, desc, min_c)

        # 5. Insertar orden de prueba inicial
        print("📦 Insertando órdenes iniciales de prueba...")
        orden1_id = await conn.fetchval("""
            INSERT INTO ordenes (order_id, telefono_cliente, pais, subtotal_usd, descuento_usd, envio_usd, total_usd, estado, metodo_pago)
            VALUES ('ORD-INIT01', '+593991234567', '593', 65.00, 6.50, 0.00, 58.50, 'ENTREGADO', 'WhatsApp / Contraentrega')
            RETURNING id
        """)
        await conn.execute("""
            INSERT INTO orden_items (orden_id, sku, nombre, talla, color, cantidad, precio_unitario, subtotal)
            VALUES ($1, 'HOOD-CYBER-M', 'Hoodie Cyberpunk Oversize', 'M', 'Negro/Rosa Neón', 1, 65.00, 65.00)
        """, orden1_id)

        print("\n" + "="*80)
        print("✅ ¡BASE DE DATOS POBLADA CON ÉXITO!")
        print("="*80)
        print(f"✨ {len(prendas)} productos principales creados con sus respectivas variantes.")
        print("🎟️  Cupones activos: NEON10 (10%), CYBER20 (20%), ENVIOGRATIS.")
        print("="*80 + "\n")

    except Exception as e:
        print(f"❌ Error al poblar base de datos: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(poblar_catalogo_masivo())