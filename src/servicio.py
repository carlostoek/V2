from dataclasses import dataclass

@dataclass
class Servicio:
    id: str
    nombre: str
    descripcion: str
    endpoint: str