import os
import subprocess

def matar_proceso_puerto(puerto):
    print(f"Buscando proceso en puerto {puerto}...")
    
    # Encontrar el PID
    result = subprocess.run(
        f'netstat -ano | findstr :{puerto}',
        shell=True, 
        capture_output=True, 
        text=True
    )
    
    if result.stdout:
        line = result.stdout.strip().split('\n')[0]
        pid = line.split()[-1]
        print(f"Proceso encontrado - PID: {pid}")
        
        # Matar el proceso
        subprocess.run(f'taskkill /PID {pid} /F', shell=True)
        print(f"✅ Proceso {pid} terminado")
    else:
        print(f"No hay procesos en el puerto {puerto}")

if __name__ == "__main__":
    matar_proceso_puerto(8000)