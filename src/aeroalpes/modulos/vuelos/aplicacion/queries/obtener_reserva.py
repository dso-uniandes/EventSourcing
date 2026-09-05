from aeroalpes.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from aeroalpes.seedwork.aplicacion.queries import ejecutar_query as query
from aeroalpes.modulos.vuelos.dominio.entidades import Reserva
from dataclasses import dataclass
from .base import ReservaQueryBaseHandler
from aeroalpes.modulos.vuelos.aplicacion.mapeadores import MapeadorReserva

@dataclass
class ObtenerReserva(Query):
    id: str = None
    estado: str = None
    id_cliente: str = None

class ObtenerReservaHandler(ReservaQueryBaseHandler):

    def handle(self, query: ObtenerReserva) -> QueryResultado:
        vista = self.fabrica_vista.crear_objeto(Reserva)
        reservas = vista.obtener_por(id=query.id, estado=query.estado, id_cliente=query.id_cliente)
        mapeador = MapeadorReserva()

        if query.id:
            reserva = self.fabrica_vuelos.crear_objeto(reservas[0], mapeador) if reservas else None
            return QueryResultado(resultado=reserva)

        return QueryResultado(resultado=[self.fabrica_vuelos.crear_objeto(reserva, mapeador) for reserva in reservas])

@query.register(ObtenerReserva)
def ejecutar_query_obtener_reserva(query: ObtenerReserva):
    handler = ObtenerReservaHandler()
    return handler.handle(query)