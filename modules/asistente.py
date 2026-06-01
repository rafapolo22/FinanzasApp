import os
from google import genai
from google.genai import types
from modules import reportes, presupuestos
from datetime import datetime

# Configurar el Cliente de Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

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
    Usa la nueva SDK google-genai.
    """
    if not GEMINI_API_KEY or not client:
        return "Error: La API Key de Gemini no está configurada o el cliente no pudo inicializarse. Por favor, configura GEMINI_API_KEY."

    try:
        contexto = obtener_contexto_financiero(usuario_id)
        
        system_instruction = (
            "Eres un asistente financiero experto llamado 'FinanzasAI'. "
            "Tu objetivo es ayudar al usuario a entender sus finanzas personales basándote en los datos que se te proporcionan. "
            "Sé amable, profesional y da consejos prácticos para ahorrar o gestionar mejor el dinero. "
            "Si el usuario te pregunta algo no relacionado con finanzas, trata de llevar la conversación de vuelta a sus finanzas de forma educada."
        )

        # Configuración de generación
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            top_p=0.95,
            top_k=64,
            max_output_tokens=1024,
            http_options={'timeout': 30000} # Timeout en milisegundos para google-genai
        )

        full_prompt = f"{contexto}\n\nMensaje del usuario: {mensaje_usuario}"
        
        # Llamada a la API usando la nueva SDK
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=full_prompt,
            config=config
        )
        
        if not response or not response.text:
            return "El asistente no pudo generar una respuesta en este momento. Inténtalo de nuevo."

        return response.text

    except Exception as e:
        error_msg = str(e)
        print(f"Error en chat_con_asistente: {error_msg}")
        
        if "quota" in error_msg.lower() or "429" in error_msg:
            return "Se ha superado el límite de consultas a la API. Por favor, espera un momento antes de volver a preguntar."
        elif "deadline" in error_msg.lower() or "timeout" in error_msg.lower():
            return "La consulta tardó demasiado tiempo. Por favor, intenta con una pregunta más corta o verifica tu conexión."
        
        return f"Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intenta más tarde."
