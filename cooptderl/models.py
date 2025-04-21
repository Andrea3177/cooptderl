from . import db
from flask_login import UserMixin


######################### USUARIOS EN LA WEB (OMR) #########################
class RolUs(db.Model): 
    tablename = 'rol_us' 
    rol_us_code = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    have_book = db.Column(db.Boolean, nullable=False) 
    perm_delete = db.Column(db.Boolean, nullable=False) 
    perm_change = db.Column(db.Boolean, nullable=False) 
    per_create = db.Column(db.Boolean, nullable=False) 
    perm_authorization = db.Column(db.Boolean, nullable=False) 
    users = db.relationship("User", back_populates="rol")

class User(UserMixin, db.Model): 
    tablename = 'user' 
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    name_user = db.Column(db.String(25), nullable=False) 
    email = db.Column(db.String(250)) 
    password = db.Column(db.String(10), nullable=False) 
    rol_us_ = db.Column(db.Integer, db.ForeignKey('rol_us.rol_us_code'), nullable=False) 
    rol = db.relationship("RolUs", back_populates="users")
    def get_id(self):
        return self.id_user

######################## INFO EXTRA ############################

class Pais(db.Model):
    __tablename__ = 'pais'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(35))

class Depto(db.Model):
    __tablename__ = 'depto'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(35))
    pais = db.Column(db.Integer, db.ForeignKey('pais.id'))

    relacion_pais = db.relationship("Pais")

class Municipio(db.Model):
    __tablename__ = 'municipio'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(35))
    depto = db.Column(db.Integer, db.ForeignKey('depto.id'))

    depto_rel = db.relationship("Depto")

class Distrito(db.Model):
    __tablename__ = 'distrito'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(35))
    municipio = db.Column(db.Integer, db.ForeignKey('municipio.id'))

    municipio_rel = db.relationship("Municipio")

class TipoEmpresa(db.Model):
    __tablename__ = 'tipo_empresa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(35))

class LineaCred(db.Model):
    __tablename__ = 'linea_cred'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(35))
    interes_m = db.Column(db.Float)

class PeriodoCred(db.Model):
    __tablename__ = 'periodo_cred'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(35))
    dias = db.Column(db.Integer)

############# INFO DE CLIENTE OMR #################

class Asociado(db.Model):
    __tablename__ = 'asociados'
    id_as = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_as = db.Column(db.String(30))
    apellidos_as = db.Column(db.String(30))
    apellido_cas_as = db.Column(db.String(10))
    genero_as = db.Column(db.String(20))
    pais_nacimiento = db.Column(db.Integer, db.ForeignKey('pais.id'))
    depto_nacimiento = db.Column(db.Integer, db.ForeignKey('depto.id'))
    municipio_nacimiento = db.Column(db.Integer, db.ForeignKey('municipio.id'))
    fecha_nacimiento = db.Column(db.Date)
    tipo_vivienda = db.Column(db.String(30))
    tiempo_residir = db.Column(db.Integer)
    estado_civil = db.Column(db.String(30))
    profesion_oficio = db.Column(db.String(40))
    actividad_economica = db.Column(db.String(35))
    correo_as = db.Column(db.String(50))
    numero_telefono_as = db.Column(db.String(15))
    doc_identidad_as = db.Column(db.Integer, unique=True)
    tipo_doc_identidad = db.Column(db.String(20))
    ISS_as = db.Column(db.String(255))
    NUP_as = db.Column(db.String(255))
    n_dependientes_economicamente = db.Column(db.Integer)


    pais = db.relationship("Pais")
    depto = db.relationship("Depto")
    municipio = db.relationship("Municipio")
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Beneficiario(db.Model):
    __tablename__ = 'beneficiarios'
    id_beneficiario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    relacion_con_as = db.Column(db.String(25))
    nombre_ben = db.Column(db.String(15))
    apellidos_ben = db.Column(db.String(15))
    num_telefono = db.Column(db.String(15))

    asociado = db.relationship("Asociado")

class Referencia(db.Model):
    __tablename__ = 'referencias'
    id_ref = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    relacion_con_as = db.Column(db.String(25))
    nombre_ref = db.Column(db.String(15))
    apellidos_ref = db.Column(db.String(15))
    nacionalidad = db.Column(db.String(25))
    num_telefono = db.Column(db.String(15))

    asociado = db.relationship("Asociado")

class Admision(db.Model):
    __tablename__ = 'admisiones'
    id_admision = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_de_admi = db.Column(db.Date)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    tipo_ingreso_ad = db.Column(db.String(13))

    asociado = db.relationship("Asociado")

class Residencia(db.Model):
    __tablename__ = 'residencia'
    id_res = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    pais_res = db.Column(db.Integer, db.ForeignKey('pais.id'))
    depto_res = db.Column(db.Integer, db.ForeignKey('depto.id'))
    municipio_res = db.Column(db.Integer, db.ForeignKey('municipio.id'))
    direccion_res = db.Column(db.String(70))

    asociado = db.relationship("Asociado")
    pais = db.relationship("Pais")
    depto = db.relationship("Depto")
    municipio = db.relationship("Municipio")

class DocIdentidad(db.Model):
    __tablename__ = 'doc_identidad'
    numero_doc = db.Column(db.String(14), primary_key=True)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    tipo_doc = db.Column(db.String(2))
    fecha_vencimiento = db.Column(db.Date)

    asociado = db.relationship("Asociado")

class Ingreso(db.Model):
    __tablename__ = 'ingresos'
    id_ingreso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    ingreso_empresa = db.Column(db.Float)
    pension = db.Column(db.Float)
    remesas = db.Column(db.Float)
    arrendamientos = db.Column(db.Float)
    detalles_de_otros = db.Column(db.String(30))
    otros = db.Column(db.Float)

    asociado = db.relationship("Asociado")

class Empresa(db.Model):
    __tablename__ = 'empresa'
    id_empresa = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_empresa = db.Column(db.String(60))
    tipo_empresa = db.Column(db.Integer, db.ForeignKey('tipo_empresa.id'))
    NIT_empresa = db.Column(db.String(15))
    act_economica = db.Column(db.String(35))
    NRC_empresa = db.Column(db.String(255))
    direccion_empresa = db.Column(db.String(70))
    relacion_comercial_gob = db.Column(db.Boolean)
    recibir_sancion = db.Column(db.Boolean)

    tipo_empresa_rel = db.relationship("TipoEmpresa")


class EmpresaPropia(db.Model):
    __tablename__ = 'empresa_propia'
    id_empresa_propia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'))

    asociado = db.relationship("Asociado")
    empresa = db.relationship("Empresa")

class TrabajoIngreso(db.Model):
    __tablename__ = 'trabajo_ingreso'
    id_trabajo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    salario_mensual = db.Column(db.Float)
    contacto_laboral = db.Column(db.String(15))
    fecha_ingreso = db.Column(db.Time)
    cargo = db.Column(db.String(15))
    nombre_jefe_inmediato = db.Column(db.String(45))

    asociado = db.relationship("Asociado")

###### MOVIMIENTOS DE DINERO(OMR, CREDITOS, AHORROS, APORTACIONES, ETC) ########

class Credito(db.Model):
    __tablename__ = 'creditos'
    id_credito = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    linea_cred = db.Column(db.Integer, db.ForeignKey('linea_cred.id'))
    periodo_cred = db.Column(db.Integer, db.ForeignKey('periodo_cred.id'))
    plazo_cred = db.Column(db.Integer)
    rotativo_cred = db.Column(db.Boolean)
    aprobado_cred = db.Column(db.Boolean)
    fecha_aprob_cred = db.Column(db.Date)
    liquidado_cred = db.Column(db.Boolean)
    liquidacion_cred = db.Column(db.Date)
    cancelado_cred = db.Column(db.Boolean)
    Limite_credito = db.Column(db.Float)

    asociado = db.relationship("Asociado")
    linea_credito = db.relationship("LineaCred")
    periodo_credito = db.relationship("PeriodoCred")

class Ahorros(db.Model):
    __tablename__ = 'ahorros'
    id_ahorros = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    apertura_ahorros = db.Column(db.Date)
    linea_ahorros = db.Column(db.String(10))
    Interes_mensual = db.Column(db.Float)
    final_ahorros = db.Column(db.Date)

    asociado = db.relationship("Asociado")


class CuotaIngreso(db.Model):
    __tablename__ = 'cuota_ingreso'
    id_cuota_ingreso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    id_transaccion = db.Column(db.Integer)
    cuota_ingreso = db.Column(db.Float)
    forma_pago = db.Column(db.String(15))
    responsable_us = db.Column(db.Integer)

    asociado = db.relationship("Asociado")

class FianzaCol(db.Model):
    __tablename__ = 'fianza_col'
    id_fianza_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    monto =db.Column(db.Float)
    responsable_us = db.Column(db.Integer)
    forma_pago = db.Column(db.String(15))
    credito = db.Column(db.Integer, db.ForeignKey('creditos.id_credito'))

    credito_rel = db.relationship("Credito")
    asociado = db.relationship("Asociado")

class TransaccionAhorros(db.Model):
    __tablename__ = 'transaccion_ahorros'
    id_transaccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_ahorros = db.Column(db.Integer, db.ForeignKey('ahorros.id_ahorros'))
    ingreso = db.Column(db.Float)
    egreso = db.Column(db.Float)
    fecha = db.Column(db.Date)
    dias = db.Column(db.Integer)
    intereses_pendientes = db.Column(db.Float)
    responsable_us = db.Column(db.Integer, db.ForeignKey('user.id_user'))
    saldo_restante = db.Column(db.Float)
    comentario = db.Column(db.String(500))
    forma_pago = db.Column(db.String(15))

    ahorros = db.relationship("Ahorros")
    responsable = db.relationship("User")

class TransaccionAportaciones(db.Model):
    __tablename__ = 'transaccion_aportaciones'
    id_transaccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date)
    id_as = db.Column(db.Integer, db.ForeignKey('asociados.id_as'))
    ingreso = db.Column(db.Float)
    egreso = db.Column(db.Float)
    saldo_restante = db.Column(db.Float)
    responsable_us = db.Column(db.Integer, db.ForeignKey('user.id_user'))
    forma_pago = db.Column(db.String(15))
    comentario = db.Column(db.String(500))

    responsable = db.relationship("User")

class MovimientosCredito(db.Model):
    __tablename__ = 'movimientos_credito'
    id_movimiento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_credito = db.Column(db.Integer, db.ForeignKey('creditos.id_credito'))
    fecha = db.Column(db.Date)
    dias = db.Column(db.Integer)
    abono = db.Column(db.Float)
    intereses_abono = db.Column(db.Float, default=None)
    capital_abono = db.Column(db.Float, default=None)
    retiro_cant = db.Column(db.Float, default=None)
    saldo_restante = db.Column(db.Float)
    intereses_restantes = db.Column(db.Float)
    responsable_us = db.Column(db.Integer, db.ForeignKey('user.id_user'))
    forma_pago = db.Column(db.String(15))
    comentario = db.Column(db.String(500))

    credito = db.relationship("Credito")
    responsable = db.relationship("User")

class Booking(db.Model):
    __tablename__ = 'booking'
    id_transaccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    income = db.Column(db.Float)
    outcome = db.Column(db.Float)
    date_ = db.Column(db.DateTime)
    responsable = db.Column(db.Integer, db.ForeignKey('user.id_user'))
    saldo_restante = db.Column(db.Float)

    responsable_user = db.relationship("User")


from datetime import datetime

########################## OTROS #######################################

def calcular_intereses_pendientes(saldo_actual, interes_mensual, fecha_ultima_transaccion, fecha_actual):
    
    dias_intereses = (fecha_actual - fecha_ultima_transaccion).days
    interes_mensual = interes_mensual / 100
    interes_mensual = round(interes_mensual, 2)
    if dias_intereses < 0:
        raise ValueError("La fecha de la última transacción no puede ser en el futuro.")

    tasa_diaria = interes_mensual / 30  
    intereses_acumulados = saldo_actual * tasa_diaria * dias_intereses
    intereses_acumulados = round(intereses_acumulados, 2)
    return intereses_acumulados, dias_intereses
