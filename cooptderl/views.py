from flask_login import login_user, current_user, login_required, logout_user
from flask import request, url_for, redirect, render_template, session, jsonify
from .models import User, Asociado, TransaccionAportaciones, Ahorros, TransaccionAhorros, calcular_intereses_pendientes, Booking, Credito, LineaCred, PeriodoCred, MovimientosCredito
from . import ses, app, login_manager
from sqlalchemy import or_
from sqlalchemy.orm import joinedload   
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def get_layout_for_user(user):
    if user.is_authenticated and (user.rol_us_ == 1 or user.rol_us_ == 2):
        return 'layout_admin.html'
    else:
        return 'layout.html'


# LOGIN MANAGER
@login_manager.user_loader
def load_user(user_id):
    user = ses.query(User).get(int(user_id))
    if user:
        print("everything okay")
        return user
    return None

@login_manager.request_loader
def load_user_from_request(request):
    user_id = request.cookies.get('user_id')
    if user_id:
        return load_user(user_id)
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname_form']
        passwd = request.form['password_form']

        actual_user = ses.query(User).filter_by(name_user=nickname).first()

        if actual_user and actual_user.password == passwd:
            login_user(actual_user)
            print(f"Usuario {actual_user.name_user} ha iniciado sesion")
            print(f"Usuario actual despues de login: {current_user}")

            session.permanent = True
            session['username'] = actual_user.name_user

            next_page = session.pop('next', url_for('home'))
            return redirect(next_page)
        else:
            mensaje = "Usuario o contrasenia incorrectos"
            return redirect(url_for('mjs', mensaje=mensaje))
    
    layout = get_layout_for_user(current_user)
    return render_template('login.html', layout=layout)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


############################  PRINCIPAL VIEWS  ###################################

@app.route('/home')
@login_required
def home():
    layout = get_layout_for_user(current_user)
    print('Home')
    return render_template('index.html', layout=layout)

@app.route('/mjs')
def mjs():
    mensaje = request.args.get('mensaje', '')
    layout = get_layout_for_user(current_user)
    return render_template('mjs.html', mensaje=mensaje, layout=layout)


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    search_results = []

    if query:
        search_results = ses.query(Asociado).filter(
            or_(
                Asociado.nombre_as.like(f'%{query}%'),
                Asociado.apellidos_as.like(f'%{query}%'),
                Asociado.apellido_cas_as.like(f'%{query}%')
            )
        ).all()

    layout = get_layout_for_user(current_user)
    print('search results: ',search_results)
    return render_template('search.html', query=query, results=search_results, layout=layout)

###################### ASOCIADOS ########################################

@app.route('/agregar_cliente', methods=['GET', 'POST'])
@login_required
def agregar_cliente():
    layout = get_layout_for_user(current_user)

    if request.method == 'POST':
        try:
            nuevo = Asociado(
                nombre_as=request.form['nombre_as'],
                apellidos_as=request.form['apellidos_as'],
                apellido_cas_as=request.form['apellido_cas_as'],
                genero_as=request.form['genero_as'],
                fecha_nacimiento=request.form['fecha_nacimiento'],
                estado_civil=request.form['estado_civil'],
                profesion_oficio=request.form['profesion_oficio'],
                actividad_economica=request.form['actividad_economica'],
                correo_as=request.form['correo_as'],
                numero_telefono_as=request.form['numero_telefono_as'],
                doc_identidad_as=request.form['doc_identidad_as']
            )
            ses.add(nuevo)
            ses.commit()
            return redirect(url_for('mjs', mensaje="Cliente agregado correctamente"))
        except Exception as e:
            ses.rollback()
            print(e)
            return "Error al agregar cliente", 500

    return render_template('agregar_cliente.html', layout=layout)



@app.route('/detalle_asociado/<id_as>', methods=['GET'])
@login_required
def detalle_asociado(id_as):

    asociado = ses.query(Asociado).options(
        joinedload(Asociado.pais),
        joinedload(Asociado.depto),
        joinedload(Asociado.municipio)
        ).filter_by(id_as=id_as).first()
    
    if not asociado:
        return "Asociado no encontrado", 404
    layout=get_layout_for_user(current_user)
    return render_template('detalle_asociado.html', asociado=asociado, layout=layout)

################################## APORTACIONES ##############################

@app.route('/aportaciones/<id_as>', methods=['GET'])
@login_required
def aportaciones(id_as):
    asociado = ses.query(Asociado).get(id_as)
    layout=get_layout_for_user(current_user)

    if not asociado:
        return "Asociado no encontrado", 404
    transaccionesAportaciones = ses.query(TransaccionAportaciones).filter_by(id_as=TransaccionAportaciones.id_as).all()
    print(transaccionesAportaciones)

    return render_template('aportaciones.html', layout=layout, asociado=asociado, transaccionesAportaciones=transaccionesAportaciones)

@app.route('/agregar_aportacion/<id_as>', methods=['POST', 'GET'])
@login_required
def agregar_aportacion(id_as):
    asociado = ses.query(Asociado).get(id_as)
    layout=get_layout_for_user(current_user)
    saldo_actual = ses.query(TransaccionAportaciones).filter_by(id_as=id_as).order_by(TransaccionAportaciones.id_transaccion.desc()).first()

    if saldo_actual:
        saldo_actual = saldo_actual.saldo_restante
    else:
        saldo_actual = 0.00

    if not asociado:
        return "Asociado no encontrado", 404
    
    ingreso = request.form['ingreso'] == 'on' if 'ingreso' in request.form else False
    monto = request.form['monto']
    monto = float(monto)
    fecha = request.form['fecha']
    forma_pago = request.form['forma_pago']
    comentario = request.form['comentario']

    nueva_aportacion=TransaccionAportaciones(
        id_as=id_as,
        fecha=fecha,          
        ingreso=monto if ingreso else 0,
        egreso=monto if not ingreso else 0,
        saldo_restante = saldo_actual + monto if ingreso else saldo_actual - monto,
        responsable_us = current_user.id_user,
        forma_pago = forma_pago,
        comentario = comentario)
    
    if nueva_aportacion.saldo_restante < 0:
        return redirect(url_for('mjs', mensaje="Saldo insuficiente"))
    last_booking = ses.query(Booking).order_by(Booking.responsable.desc()).first()
    if not last_booking:
        last_booking = 0.00
    else:
        last_booking = last_booking.saldo_restante
    booking = Booking(
        income = nueva_aportacion.ingreso,
        outcome = nueva_aportacion.egreso,
        date_ = fecha,
        responsable = current_user.id_user,
        saldo_restante = last_booking + nueva_aportacion.ingreso - nueva_aportacion.egreso
    )
    print('booking: ', booking)
    try:
        ses.add_all([nueva_aportacion, booking])
        ses.commit()
    except Exception as e:
        ses.rollback()
        print(e)
        return "Error al agregar aportacion", 500
    
    return redirect(url_for('aportaciones', id_as=id_as, layout=layout))


#########################AHORROS##############################################

@app.route('/ahorros/<id_as>', methods=['GET'])
@login_required
def ahorros(id_as):
    asociado = ses.query(Asociado).get(id_as)
    ahorros = ses.query(Ahorros).filter_by(id_as=id_as).all()
    layout=get_layout_for_user(current_user)
    if not asociado:
        return "Asociado no encontrado", 404
    return render_template('ahorros.html', layout=layout, asociado=asociado, ahorros=ahorros)

@app.route('/nuevos_ahorros/<id_as>', methods=['POST', 'GET'])
@login_required
def nuevos_ahorros(id_as):
    apertura_ahorros = request.form['fecha']
    linea_ahorros = request.form['linea_ahorros']
    interes_m = request.form['interes_m']
    final_ahorros = request.form['final_ahorros']

    nuevos_ahorros = Ahorros(
        id_as=id_as,
        apertura_ahorros=apertura_ahorros,
        linea_ahorros=linea_ahorros,
        Interes_mensual=interes_m,
        final_ahorros=final_ahorros
    )

    try:
        ses.add(nuevos_ahorros)
        ses.commit()
    except Exception as e:
        ses.rollback()
        print(e)
        return "Error al agregar ahorros", 500
    
    return redirect(url_for('ahorros', id_as=id_as))

@app.route('/detalle_ahorros/<id_ahorros>', methods=['GET', 'POST'])
@login_required
def detalle_ahorros(id_ahorros):
    ahorros = ses.query(Ahorros).get(id_ahorros)
    transacciones = ses.query(TransaccionAhorros).filter_by(id_ahorros=id_ahorros).all()
    print(transacciones)
    asociado = ses.query(Asociado).get(ahorros.id_as)
    layout=get_layout_for_user(current_user)
    if not ahorros:
        return "Ahorros no encontrados", 404
    if request.method == 'POST':
        ingreso = request.form['ingreso'] == 'on' if 'ingreso' in request.form else False
        monto = request.form['monto']
        monto = float(monto)
        fecha = request.form['fecha']
        forma_pago = request.form['forma_pago']
        comentario = request.form['comentario']

        transaccion = ses.query(TransaccionAhorros).filter_by(id_ahorros=id_ahorros).order_by(TransaccionAhorros.id_transaccion.desc()).first()
        ahorros = ses.query(Ahorros).get(id_ahorros)
        dias = 0
        intereses_pendientes = 0
        saldo_actual = 0
        if  transaccion:
            hoy = datetime.now()
            nuevos_intereses, dias = calcular_intereses_pendientes(interes_mensual=ahorros.Interes_mensual, saldo_actual=transaccion.saldo_restante, fecha_ultima_transaccion=transaccion.fecha, fecha_actual=hoy.date())
            
            intereses_pendientes = intereses_pendientes + nuevos_intereses
            saldo_actual = transaccion.saldo_restante

        nueva_transaccion = TransaccionAhorros(
            id_ahorros=id_ahorros,
            fecha=fecha,
            ingreso=monto if ingreso else 0,
            egreso=monto if not ingreso else 0,
            saldo_restante = saldo_actual + monto if ingreso else saldo_actual - monto,
            intereses_pendientes = intereses_pendientes,
            responsable_us = current_user.id_user,
            forma_pago = forma_pago,
            comentario = comentario,
            dias = dias)
        last_booking = ses.query(Booking).order_by(Booking.responsable.desc()).first()
        if last_booking:
            last_booking = last_booking.saldo_restante
        else:
            last_booking = 0.00

        booking = Booking(
            income = nueva_transaccion.ingreso,
            outcome = nueva_transaccion.egreso,
            date_ = fecha,
            responsable = current_user.id_user,
            saldo_restante = last_booking + nueva_transaccion.ingreso - nueva_transaccion.egreso
        )
        print(booking)

        try:
            ses.add_all([nueva_transaccion, booking])
            ses.commit()
        except Exception as e:
            ses.rollback()
            print(e)
            return "Error al agregar transaccion", 500
        return redirect(url_for('detalle_ahorros', id_ahorros=id_ahorros))

    return render_template('transacciones_ahorros.html', asociado=asociado, layout=layout, ahorros=ahorros, transacciones = transacciones)

@app.route('/pagar_intereses_ahorros/<id_ahorros>', methods=['GET'])
@login_required
def pagar_intereses_ahorros(id_ahorros):
    ahorros = ses.query(Ahorros).get(id_ahorros)
    transacciones = ses.query(TransaccionAhorros).filter_by(id_ahorros=id_ahorros).order_by(TransaccionAhorros.id_transaccion.desc()).first()
    hoy = datetime.now()
    hoy = hoy.date()
    print(transacciones.fecha)
    if not transacciones:
        return "No hay intereses que calcular", 404
    hoy = datetime.now()
    nuevos_intereses, dias = calcular_intereses_pendientes(interes_mensual=ahorros.Interes_mensual, fecha_ultima_transaccion=transacciones.fecha, saldo_actual = transacciones.saldo_restante, fecha_actual=hoy.date())
    intereses_pendientes_actuales = transacciones.intereses_pendientes
    nuevo_monto = transacciones.saldo_restante + intereses_pendientes_actuales + nuevos_intereses
    transaccion = TransaccionAhorros(
        id_ahorros=id_ahorros,
        fecha=datetime.now(),
        ingreso=0,
        egreso=0,
        saldo_restante=round(nuevo_monto, 2),
        intereses_pendientes=0,
        responsable_us=current_user.id_user,
        comentario="Pago de intereses",
        forma_pago="",
        dias=dias
    )

    try:    
        ses.add(transaccion)
        ses.commit()
    except Exception as e:
        ses.rollback()
        print(e)
        return "Error al pagar intereses", 500
    return redirect(url_for('detalle_ahorros', id_ahorros=id_ahorros))

#########################CREDITOS##############################################

@app.route('/creditos/<id_as>', methods=['GET', 'POST'])
@login_required
def creditos(id_as):
    asociado = ses.query(Asociado).get(id_as)
    layout=get_layout_for_user(current_user)
    creditos = ses.query(Credito).options(
        joinedload(Credito.linea_credito),
        joinedload(Credito.periodo_credito),
    ).filter_by(id_as=id_as).all()
    

    lineas = ses.query(LineaCred).all()
    periodos = ses.query(PeriodoCred).all()
    if not asociado:
        return "Asociado no encontrado", 404
    
    if request.method == 'POST':
        linea_cred = request.form['linea_cred']
        periodo_cred = request.form['periodo_cred']
        plazo_cred = request.form['plazo_cred']
        rotativo_cred = request.form['rotativo_cred'] == 'true'
        aprobado_cred = request.form['aprobado_cred'] == 'true'
        fecha_aprob_cred = datetime.strptime(request.form['fecha_aprob_cred'], '%Y-%m-%d')
        liquidado_cred = request.form['liquidado_cred'] == 'true'
        liquidacion_cred = request.form['liquidacion_cred']
        cancelado_cred = request.form['cancelado_cred'] == 'true'
        limite_credito = float(request.form['limite_credito'])

        nuevo_credito = Credito(
            id_as=id_as,
            linea_cred=linea_cred,
            periodo_cred=periodo_cred,
            plazo_cred=plazo_cred,
            rotativo_cred=rotativo_cred,
            aprobado_cred=aprobado_cred,
            fecha_aprob_cred=fecha_aprob_cred,
            liquidado_cred=liquidado_cred,
            liquidacion_cred=datetime.strptime(liquidacion_cred, '%Y-%m-%d') if liquidacion_cred else None,
            cancelado_cred=cancelado_cred,
            Limite_credito=limite_credito
        )

        try:
            ses.add(nuevo_credito)
            ses.commit()
            return redirect(url_for('creditos', id_as=id_as))
        except Exception as e:
            ses.rollback()
            print(f"Error al guardar el crédito: {e}")
            return "Error al guardar el crédito", 500


    return render_template('creditos.html', layout=layout, asociado=asociado, creditos=creditos, lineas=lineas, periodos=periodos)


@app.route('/detalle_credito/<int:id_credito>', methods=['GET', 'POST'])
@login_required
def detalle_credito(id_credito):
    # Obtener el crédito y validar si existe
    credito = ses.get(Credito, id_credito)
    if not credito:
        return "Crédito no encontrado", 404

    asociado = ses.get(Asociado, credito.id_as)
    layout = get_layout_for_user(current_user)

    transacciones = (
        ses.query(MovimientosCredito)
        .filter_by(id_credito=id_credito)
        .order_by(MovimientosCredito.fecha.desc())
        .all()
    )
    u_transaccion = (
        ses.query(MovimientosCredito)
        .filter_by(id_credito=id_credito)
        .order_by(MovimientosCredito.id_movimiento.desc())
        .first()
    )

    calcular_int = request.args.get('extra_params', None)

    # Calcular intereses al día
    intereses_al_día, dias_al_dia = 0, 0
    if u_transaccion:
        try:
            hoy = datetime.now().date()
            intereses_al_día, dias_al_dia = calcular_intereses_pendientes(
                interes_mensual=credito.linea_credito.interes_m,
                fecha_ultima_transaccion=u_transaccion.fecha,
                saldo_actual=u_transaccion.saldo_restante,
                fecha_actual=hoy
            )
            intereses_al_día = round(intereses_al_día + u_transaccion.intereses_restantes, 2)
        except Exception as e:
            print("Error al calcular intereses:", e)

    # Procesar formulario POST
    if request.method == 'POST':
        try:
            retiro = 'ingreso' in request.form and request.form['ingreso'] == 'on'
            monto = round(float(request.form['monto']), 2)
            fecha = datetime.strptime(request.form['fecha'], "%Y-%m-%d").date()
            forma_pago = request.form['forma_pago']
            comentario = request.form['comentario']
            intereses_pendientes = round(float(request.form['interes']), 2)

            # Cálculo de abono a capital e intereses
            if retiro:
                if intereses_pendientes > monto:
                    intereses_pendientes_pagados = round(intereses_pendientes - monto, 2)
                    capital_abono = 0
                else:
                    capital_abono = round(monto - intereses_pendientes, 2)
                    intereses_pendientes_pagados = intereses_pendientes
            else:
                intereses_pendientes_pagados = 0
                capital_abono = 0

            # Calcular saldo restante correctamente
            saldo_restante = round(
                (u_transaccion.saldo_restante - capital_abono) if retiro
                else (u_transaccion.saldo_restante - monto),
                2
            ) if u_transaccion else round(monto if not retiro else 0, 2)

            # Crear nueva transacción de crédito
            mov_credito = MovimientosCredito(
                id_credito=id_credito,
                fecha=fecha,
                dias=dias_al_dia,
                abono=round(monto if retiro else 0, 2),
                intereses_abono= intereses_pendientes_pagados,
                capital_abono= capital_abono,
                retiro_cant=round(monto if not retiro else 0, 2),
                saldo_restante=saldo_restante,
                intereses_restantes=round(intereses_pendientes - intereses_pendientes_pagados, 2),
                responsable_us=current_user.id_user,
                forma_pago=forma_pago,
                comentario=comentario
            )

            # Obtener último saldo del usuario en Booking
            u_book = (
                ses.query(Booking)
                .filter_by(responsable=current_user.id_user)
                .order_by(Booking.date_.desc())
                .first()
            )
            saldo_anterior = round(u_book.saldo_restante if u_book else 0, 2)

            # Crear registro en Booking
            book = Booking(
                income=mov_credito.abono,
                outcome=mov_credito.retiro_cant,
                date_=fecha,
                responsable=current_user.id_user,
                saldo_restante=round(saldo_anterior + mov_credito.abono - mov_credito.retiro_cant, 2)
            )

            # Guardar en la base de datos
            ses.add_all([mov_credito, book])
            ses.commit()

        except SQLAlchemyError as e:
            ses.rollback()
            print("Error al guardar la transacción:", e)
            return "Error al agregar transacción", 500

        return redirect(url_for('detalle_credito', id_credito=id_credito))

    return render_template(
        'transacciones_credito.html',
        layout=layout,
        asociado=asociado,
        credito=credito,
        transacciones=transacciones,
        u_transaccion=u_transaccion,
        intereses_al_día=intereses_al_día,
        dias_al_dia=dias_al_dia,
        calcular_int=calcular_int
    )


@app.route('/calcular_intereses', methods=['POST'])
def calcular_intereses():
    data = request.get_json()
    fecha_str = data.get('fecha')
    id_credito = data.get('id_credito')

    if not fecha_str or not id_credito:
        return jsonify({'error': 'Fecha o ID de crédito no proporcionado'}), 400

    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    fecha = fecha.date()

    # Obtener la última transacción del crédito
    u_transaccion = ses.query(MovimientosCredito).filter_by(id_credito=id_credito).order_by(MovimientosCredito.id_movimiento.desc()).first()

    if not u_transaccion:
        return jsonify({'error': 'No hay transacciones previas'}), 400

    # Calcular intereses hasta la fecha proporcionada
    intereses_al_dia, _ = calcular_intereses_pendientes(
        interes_mensual=u_transaccion.credito.linea_credito.interes_m,
        fecha_ultima_transaccion=u_transaccion.fecha,
        saldo_actual=u_transaccion.saldo_restante,
        fecha_actual=fecha
    )

    return jsonify({'intereses_al_dia': intereses_al_dia})

