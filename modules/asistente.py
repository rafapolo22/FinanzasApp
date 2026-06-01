import os
import google.generativeai as genai
from modules import reportes, presupuestos
from datetime import datetime

# Configurar la API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def obtener_contexto_financiero(usuario_id):
    """
    Recopila balance, top gastos y presupuestos para enviarlos a la IA.
    """
    ahora = datetime.now()
    balance = reportes.balance_mensual(usuario_id, ahora.month, ahora.year)
    top_gastos = reportes.top_gastos(usuario_id)
    mis_presupuestos = presupuestos.listar_presupuestos(usuario_id)
    alertas = presupuestos.verificar_alertas(usuario_id)

    # Formatear el contexto como texto
    contexto = f"--- CONTEXTO FINANCIERO DEL USUARIO ---\n"
    contexto += f"Fecha actual: {ahora.strftime('%d/%m/%Y')}\n"
    contexto += f"Balance del mes ({ahora.strftime('%B %Y')}):\n"
    contexto += f"  - Ingresos: ${balance['ingresos']:.2f}\n"
    contexto += f"  - Gastos: ${balance['gastos']:.2f}\n"
    contexto += f"  - Balance Neto: ${balance['balance']:.2f}\n\n"

    contexto += "Top 5 Gastos Recientes:\n"
    for g in top_gastos:
        contexto += f"  - {g['fecha']}: {g['categoria']} - ${g['monto']:.2f} ({g['descripcion']})\n"
    
    contexto += "\nPresupuestos y Alertas:\n"
    if not mis_presupuestos:
        contexto += "  - No hay presupuestos configurados.\n"
    for p in mis_presupuestos:
        contexto += f"  - {p['nombre_categoria']}: Límite de ${p['monto_limite']:.2f} ({p['periodo']})\n"
    
    for a in alertas:
        contexto += f"  - ALERTA: Has gastado ${a['gasto_real']:.2f} de ${a['limite']:.2f} en {a['categoria']} ({a['porcentaje']:.1f}%)\n"
    
    return contexto

def chat_con_asistente(usuario_id, mensaje_usuario, historial=None):
    """
    Envía el mensaje del usuario a Gemini junto con el contexto financiero.
    """
    if not GEMINI_API_KEY:
        return "Error: La API Key de Gemini no está configurada. Por favor, configura GEMINI_API_KEY en las variables de entorno."

    try:
        contexto = obtener_contexto_financiero(usuario_id)
        
        # Configuración del modelo
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_instruction = (
            "Eres un asistente financiero experto llamado 'FinanzasAI'. "
            "Tu objetivo es ayudar al usuario a entender sus finanzas personales basándote en los datos que se te proporcionan. "
            "Sé amable, profesional y da consejos prácticos para ahorrar o gestionar mejor el dinero. "
            "Si el usuario te pregunta algo no relacionado con finanzas, trata de llevar la conversación de vuelta a sus finanzas de forma educada."
        )

        full_prompt = f"{system_instruction}\n\n{contexto}\n\nMensaje del usuario: {mensaje_usuario}"
        
        # En una versión más avanzada podríamos usar el historial de chat de Gemini
        response = model.generate_content(full_prompt)
        
        return response.text
    except Exception as e:
        print(f"Error en chat_con_asistente: {e}")
        return f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}"
