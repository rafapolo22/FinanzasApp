from datetime import datetime
from modules import reportes, presupuestos

def chat_con_asistente(usuario_id, mensaje_usuario, historial=None):
    """
    Sistema de respuestas inteligentes local basado en palabras clave y datos reales.
    No utiliza APIs externas.
    """
    mensaje = mensaje_usuario.lower()
    ahora = datetime.now()
    mes_actual = ahora.month
    anio_actual = ahora.year

    try:
        # 1. Saludos
        if any(palabra in mensaje for palabra in ["hola", "buenos días", "buenas tardes", "buenas noches"]):
            return "¡Hola! Soy tu asistente financiero local. ¿En qué puedo ayudarte hoy? Puedes preguntarme sobre tu balance, tus gastos o tus presupuestos."

        # 2. Balance y Resumen
        if any(palabra in mensaje for palabra in ["balance", "resumen", "estado", "cuánto tengo", "dinero"]):
            datos = reportes.balance_mensual(usuario_id, mes_actual, anio_actual)
            return (f"Tu balance de {ahora.strftime('%B %Y')} es:\n"
                    f"- Ingresos: ${datos['ingresos']:.2f}\n"
                    f"- Gastos: ${datos['gastos']:.2f}\n"
                    f"- Neto: ${datos['balance']:.2f}\n"
                    f"{'¡Vas por buen camino!' if datos['balance'] >= 0 else 'Cuidado, tus gastos superan tus ingresos.'}")

        # 3. Gastos por Categoría
        if any(palabra in mensaje for palabra in ["gastos", "categoría", "en qué gasto", "gastado"]):
            gastos = reportes.gastos_por_categoria(usuario_id, mes_actual, anio_actual)
            if not gastos:
                return "Aún no tienes gastos registrados este mes."
            
            respuesta = f"Tus gastos por categoría en {ahora.strftime('%B')} son:\n"
            for g in gastos:
                respuesta += f"- {g['categoria']}: ${g['total']:.2f}\n"
            
            # Agregar el gasto más alto
            top = reportes.top_gastos(usuario_id, limite=1)
            if top:
                respuesta += f"\nTu gasto individual más alto fue: {top[0]['descripcion']} por ${top[0]['monto']:.2f}."
            
            return respuesta

        # 4. Presupuestos y Alertas
        if any(palabra in mensaje for palabra in ["presupuesto", "límite", "alerta", "meta"]):
            alertas = presupuestos.verificar_alertas(usuario_id)
            if not alertas:
                # Si no hay alertas, quizás solo quiera ver sus presupuestos
                lista = presupuestos.listar_presupuestos(usuario_id)
                if not lista:
                    return "No tienes presupuestos configurados. ¡Te recomiendo crear uno para controlar mejor tus gastos!"
                
                respuesta = "Tus presupuestos actuales están bajo control:\n"
                for p in lista:
                    respuesta += f"- {p['nombre_categoria']}: Límite de ${p['monto_limite']:.2f}\n"
                return respuesta
            
            respuesta = "¡Atención! Aquí tienes el estado de tus presupuestos críticos:\n"
            for a in alertas:
                respuesta += f"- {a['categoria']}: {a['estado']} ({a['porcentaje']:.1f}% consumido: ${a['gasto_real']:.2f} de ${a['limite']:.2f})\n"
            return respuesta

        # 5. Ayuda
        if any(palabra in mensaje for palabra in ["ayuda", "qué puedes hacer", "opciones", "comandos"]):
            return ("Puedo ayudarte con lo siguiente:\n"
                    "1. 'Balance': Ver tus ingresos y gastos totales del mes.\n"
                    "2. 'Gastos': Ver cuánto has gastado por categoría.\n"
                    "3. 'Presupuestos': Revisar si te has pasado de tus límites.\n"
                    "4. 'Top': Consultar tus transacciones más altas.")

        # 6. Top Gastos (específico)
        if "top" in mensaje or "mayores gastos" in mensaje:
            top = reportes.top_gastos(usuario_id, limite=5)
            if not top:
                return "No hay transacciones registradas."
            respuesta = "Tus 5 mayores gastos históricos son:\n"
            for t in top:
                respuesta += f"- {t['fecha'].strftime('%d/%m/%Y')}: {t['categoria']} - ${t['monto']:.2f} ({t['descripcion']})\n"
            return respuesta

        # 7. Fallback
        return ("Lo siento, no entiendo tu pregunta. Prueba consultando por tu 'balance', 'gastos' o 'presupuestos'. "
                "Si necesitas ayuda, escribe 'ayuda'.")

    except Exception as e:
        print(f"Error en asistente local: {e}")
        return "Lo siento, ocurrió un error interno al procesar tu solicitud. Por favor, intenta de nuevo más tarde."
