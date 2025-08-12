import json
from servicio_manager import ServicioManager

def main():
    # Cargar el inventario de servicios
    servicio_manager = ServicioManager('docs/LECTURA OBLIGADA!/INVENTARIO_SERVICIOS.json')
    
    # Mostrar menú de administración
    while True:
        print("\n--- Menú del Administrador ---")
        print("1. Listar Servicios")
        print("2. Conectar Servicio")
        print("3. Salir")
        
        choice = input("Seleccione una opción: ")
        
        if choice == '1':
            servicio_manager.listar_servicios()
        elif choice == '2':
            servicio_id = input("Ingrese el ID del servicio a conectar: ")
            servicio_manager.conectar_servicio(servicio_id)
        elif choice == '3':
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()