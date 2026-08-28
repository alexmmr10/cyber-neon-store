import asyncio
import os
import sys
from pathlib import Path

# Configurar salida estándar para UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import asyncpg

# Cargar variables de entorno desde .env
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

async def verificar_stock():
    print(f"📡 Conectando a {DATABASE_URL}...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        print("💡 Asegúrate de que el contenedor o servicio de PostgreSQL esté iniciado en el puerto 5433.")
        return

    try:
        variantes = await conn.fetch("""
            SELECT 
                p.nombre, 
                p.categoria, 
                v.sku, 
                v.talla, 
                v.color, 
                v.stock, 
                v.precio,
                p.activo
            FROM variantes v
            JOIN productos p ON v.producto_id = p.id
            ORDER BY p.categoria, p.nombre, v.talla
        """)
        
        print("\n" + "="*95)
        print("📦 ESTADO DEL INVENTARIO - CYBER NEÓN STORE")
        print("="*95)
        print(f"{'SKU':<15} {'PRODUCTO':<30} {'CAT':<12} {'TALLA':<6} {'COLOR':<15} {'STOCK':<7} {'PRECIO'}")
        print("-"*95)
        
        total_items = 0
        total_stock = 0
        
        for item in variantes:
            estado_stock = f"⚠️ {item['stock']}" if item['stock'] <= 5 else f"{item['stock']}"
            print(f"{item['sku']:<15} {item['nombre'][:28]:<30} {item['categoria']:<12} {item['talla']:<6} {item['color'][:14]:<15} {estado_stock:<7} ${item['precio']:<8.2f}")
            total_items += 1
            total_stock += item['stock']
        
        print("-"*95)
        print(f"Total Variantes: {total_items} | Stock Total Acumulado: {total_stock} unidades\n")

        # Resumen de Órdenes
        total_ordenes = await conn.fetchval("SELECT COUNT(*) FROM ordenes")
        recaudacion = await conn.fetchval("SELECT COALESCE(SUM(total_usd), 0) FROM ordenes")
        ordenes_estado = await conn.fetch("""
            SELECT estado, COUNT(*) as cantidad, COALESCE(SUM(total_usd), 0) as total
            FROM ordenes
            GROUP BY estado
        """)

        print("="*95)
        print("📊 RESUMEN DE VENTAS Y ESTADOS DE ÓRDENES")
        print("="*95)
        print(f"Total Órdenes Registradas: {total_ordenes} | Facturación Total: ${float(recaudacion):.2f} USD")
        for row in ordenes_estado:
            print(f"  • Estado [{row['estado']}]: {row['cantidad']} órdenes (${float(row['total']):.2f} USD)")

        # Cupones activos
        cupones = await conn.fetch("SELECT codigo, tipo, valor, descripcion FROM cupones WHERE activo = TRUE")
        print("\n🎟️  CUPONES ACTIVOS:")
        for c in cupones:
            tipo_txt = f"{int(c['valor']*100)}%" if c['tipo'] == 'porcentaje' else f"${float(c['valor']):.2f}"
            print(f"  • {c['codigo']}: {tipo_txt} ({c['descripcion']})")

        print("="*95 + "\n")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verificar_stock())