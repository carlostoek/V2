import json
from servicio import Servicio
from conector_servicios import ConectorServicios

class ServicioManager:
    def __init__(self, inventario_path):
        self.inventario_path = inventario_path
        self.servicios = self.cargar_servicios()

    def cargar_servicios(self):
        with open(self.inventario_path, 'r') as file:
            data = json.load(file)
            return [Servicio(**servicio) for servicio in data['servicios']]

    def listar_servicios(self):
        print("\nServicios Disponibles:")
        for servicio in self.servicios:
            print(f"ID: {servicio.id}, Nombre: {servicio.nombre}")

    def conectar_servicio(self, servicio_id):
        servicio = next((s for s in self.servicios if s.id == servicio_id), None)
        if servicio:
            conector = ConectorServicios()
            conector.conectar(servicio)
        else:
            print("Servicio no encontrado.")