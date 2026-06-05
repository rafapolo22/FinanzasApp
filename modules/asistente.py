import os
import time
import anthropic
from modules import reportes, presupuestos
from datetime import datetime

def obtener_contexto_financiero(usuario_id):
    """
    Recopila balance y top 3 gastos para enviarlos a la IA (versión optimizada).
    """
    ahora = datetime.now()
    balance = reportes.balance_mensual(usuario_id, ahora.month, ahora.year)
    top_gastos = reportes.top_gastos(usuario_id, limite=3)

    # Formatear el contexto como texto (más corto para ahorrar tokens)
    contexto = f"--- RESUMEN FINANCIERO ---\n"
    contexto += f"Mes: {ahora.strftime('%m/%Y')}\n"
    contexto += f"Balance: Ingresos ${balance['ingresos']:.2f}, Gastos ${balance['gastos']:.2f}, Neto ${balance['balance']:.2f}\n"

    contexto += "Top 3 Gastos:\n"
    for g in top_gastos:
        contexto += f"- {g['categoria']}: ${g['monto']:.2f} ({g['descripcion']})\n"
    
    return contexto

def chat_con_asistente(usuario_id, mensaje_usuario, historial=None):
    """
    Envía el mensaje del usuario a Anthropic Claude junto con el contexto financiero.
    Usa el modelo claude-haiku-4-5-20251001 con reintentos para límites de cuota.
    """
    # Leer la API Key e inicializar el cliente dentro de la función
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return "Error: La API Key de Anthropic no está configurada. Por favor, configura ANTHROPIC_API_KEY."
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        return f"Error al inicializar el cliente de Anthropic: {e}"

    intentos_max = 3
    espera_segundos = 5

    for intento in range(intentos_max):
        try:
            contexto = obtener_contexto_financiero(usuario_id)
            
            system_instruction = (
                "Eres un asistente financiero experto llamado 'FinanzasAI'. "
                "Tu objetivo es ayudar al usuario a entender sus finanzas personales basándote en los datos que se te proporcionan. "
                "Sé amable, profesional y da consejos prácticos para ahorrar o gestionar mejor el dinero. "
                "Si el usuario te pregunta algo no relacionado con finanzas, trata de llevar la conversación de vuelta a sus finanzas de forma educada."
            )

            full_prompt = f"{contexto}\n\nMensaje del usuario: {mensaje_usuario}"
            
            # Llamada a la API de Anthropic
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                temperature=0.7,
                system=system_instruction,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            if not message or not message.content:
                return "El asistente no pudo generar una respuesta en este momento. Inténtalo de nuevo."

            return message.content[0].text

        except Exception as e:
            error_msg = str(e)
            print(f"Error en chat_con_asistente (intento {intento + 1}/{intentos_max}): {error_msg}")
            
            # Verificar si es un error de cuota (429) para reintentar
            if ("rate_limit" in error_msg.lower() or "429" in error_msg) and intento < intentos_max - 1:
                print(f"Límite de cuota alcanzado. Reintentando en {espera_segundos} segundos...")
                time.sleep(espera_segundos)
                continue
            
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return "Se ha superado el límite de consultas a la API. Por favor, espera un momento antes de volver a preguntar."
            elif "timeout" in error_msg.lower():
                return "La consulta tardó demasiado tiempo. Por favor, intenta con una pregunta más corta o verifica tu conexión."
            
            return f"Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intenta más tarde."
