import pulsar,_pulsar  
from pulsar.schema import *
import uuid
import time
import logging
import traceback
import datetime

from aeroalpes.modulos.vuelos.infraestructura.schema.v1.eventos import EventoReservaCreada
from aeroalpes.modulos.vuelos.infraestructura.schema.v1.comandos import ComandoCrearReserva


from aeroalpes.modulos.vuelos.infraestructura.proyecciones import ProyeccionReservasLista, ProyeccionReservasTotales
from aeroalpes.modulos.vuelos.dominio.objetos_valor import EstadoReserva
from aeroalpes.seedwork.infraestructura.proyecciones import ejecutar_proyeccion
from aeroalpes.seedwork.infraestructura import utils

def suscribirse_a_eventos(app=None):
    cliente = None
    try:
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe('eventos-reserva', consumer_type=_pulsar.ConsumerType.Shared,subscription_name='aeroalpes-sub-eventos', schema=AvroSchema(EventoReservaCreada))

        while True:
            mensaje = consumidor.receive()
            evento = mensaje.value()
            datos = evento.data
            print(f'Evento recibido: {datos}')

            tipo_evento = evento.type
            if tipo_evento == 'ReservaCreada':
                ejecutar_proyeccion(ProyeccionReservasTotales(datos.fecha_creacion, ProyeccionReservasTotales.ADD), app=app)
                ejecutar_proyeccion(ProyeccionReservasLista(datos.id_reserva, datos.id_cliente, datos.estado, datos.fecha_creacion, datos.fecha_creacion), app=app)
            elif tipo_evento in ('ReservaCancelada', 'ReservaPagada', 'ReservaAprobada'):
                estados = {
                    'ReservaCancelada': EstadoReserva.CANCELADA.name,
                    'ReservaPagada': EstadoReserva.PAGADA.name,
                    'ReservaAprobada': EstadoReserva.APROBADA.name,
                }
                ejecutar_proyeccion(ProyeccionReservasLista(datos.id_reserva, None, estados[tipo_evento], None, evento.time), app=app)
            else:
                logging.warning(f'Tipo de evento no reconocido: {tipo_evento}')
                consumidor.acknowledge(mensaje)
                continue
            
            consumidor.acknowledge(mensaje)     

        cliente.close()
    except:
        logging.error('ERROR: Suscribiendose al tópico de eventos!')
        traceback.print_exc()
        if cliente:
            cliente.close()

def suscribirse_a_comandos(app=None):
    cliente = None
    try:
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe('comandos-reserva', consumer_type=_pulsar.ConsumerType.Shared, subscription_name='aeroalpes-sub-comandos', schema=AvroSchema(ComandoCrearReserva))

        while True:
            mensaje = consumidor.receive()
            print(f'Comando recibido: {mensaje.value().data}')

            consumidor.acknowledge(mensaje)     
            
        cliente.close()
    except:
        logging.error('ERROR: Suscribiendose al tópico de comandos!')
        traceback.print_exc()
        if cliente:
            cliente.close()