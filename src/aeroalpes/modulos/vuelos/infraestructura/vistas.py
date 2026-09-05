from aeroalpes.seedwork.infraestructura.vistas import Vista
from aeroalpes.modulos.vuelos.dominio.entidades import Reserva
from aeroalpes.config.db import db
from .dto import Reserva as ReservaDTO
from .mapeadores import MapeadorReserva

class VistaReserva(Vista):
    def obtener_por(self, id=None, estado=None, id_cliente=None, **kwargs) -> [Reserva]:
        params = dict()

        if id:
            params['id'] = str(id)
        
        if estado:
            params['estado'] = str(estado)
        
        if id_cliente:
            params['id_cliente'] = str(id_cliente)

        reservas_dto = db.session.query(ReservaDTO).filter_by(**params).all()
        mapeador = MapeadorReserva()
        return [mapeador.dto_a_entidad(reserva_dto) for reserva_dto in reservas_dto]
