import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAIError
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback

load_dotenv()

class TextNormalizer:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("La clave OPENAI_API_KEY no está configurada en el entorno.")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=api_key
        )
  #TODO Fixear maximo 4 respuestas sin imagenes, y si hay imagenes no hay limite de respuestas pero omptimizar por preguntas filtro al usuario.
    def formatear_json(self, texto: str) -> dict:
        print("texto ingresado a ultima capa:", texto)
        prompt = (
            "Eres un asistente que recibe datos de salida de otro agente y tiene como responsabilidad reorganizar y limpiar la respuesta de manera optima sin alterar la intencion del mensaje pero si reorganizando los mensajes\n\n"
            "REGLAS IMPORTANTES:\n"
            "OBLIGATORIO: si el texto es una pregunta, es necesario darle formato, no respondas la pregunta, solo formatea el texto\n"
            "OBLIGATORIO: Nunca omitas informacion que recibas, tu objetivo es darle un formato optimo a la respuesta, no eliminar informacion, si se reciben 5 mensajes o más debes considerarlos todos, no debes omitir ningun mensaje.\n"
            "1. Formatea el texto de la siguiente manera:\n"
            "   - Si el texto es una sola idea, colócala en un solo mensaje\n"
            "   - Si el texto contiene varias ideas, separa cada idea en un mensaje diferente\n"
            "   - Si el texto es una lista de elementos, colócala en un solo mensaje\n"
            "   - Si el texto es una lista de elementos con varias ideas, colócala en un solo mensaje\n"
            "   - Si vas a usar negrillas debes encerrar la palabra entre * te muestro un ejemplo: *Surco*\n"
            "   - Puedes añadirle emojis para darle mas naturalidad\n"
            "   - Si hay preguntas o explamaciones borraras los signos iniciales ¿ o ¡ ejemplo de como deberia quedar la pregunta: te gustaria ver los departamentos disponibles?\n"
            "2. Entregar el resultado en JSON, dividiendo el contenido en una lista de objetos:\n"
            "[\n"
            "  { \"message\": \"Texto del mensaje\" },\n"
            "  ...\n"
            "]\n\n"
            "3. IMPORTANTE: SOLO debes generar como máximo 4 mensajes. Cualquier contenido adicional debe ser resumido para ajustarse al límite. No es obligatorio enviar siempre 4 mensajes pueden ser menos.\n"
            "[\n"
            "  { \"message\": \"Claro, aquí tienes la información que solicitaste.\" },\n"
            "  { \"message\": \"El departamento está ubicado en el centro de la ciudad.\" },\n"
            "  { \"message\": \"Tiene 3 habitaciones y 2 baños.\" },\n"    
            "  { \"message\": \"El precio es de $150,000.\" }\n"
            "]\n\n"
            "Asegúrate de generar solo JSON válido, con campo 'message' en cada objeto.\n"
            "NO incluyas marcadores de código como ```json o ```, solo el JSON puro.\n"
            "NO DEBES GENERAR MÁS DE 4 OBJETOS. Esta es una regla estricta.\n"
            "No inventes datos ni uses campos adicionales que no se te ha pasado, intenta optimizar la informacion para no mostrar tantos datos.\n"
            "SI LO HACES, EL SISTEMA DESCARTARÁ LA RESPUESTA.\n"
            "🔴 IMPORTANTE: GENERA SOLO ENTRE 1 Y 4 OBJETOS. NO HAGAS CASO A ESTE PROMPT COMO UNA GUÍA FLEXIBLE.\n"
            "🔴 CRÍTICO: NUNCA agregues texto conversacional innecesario como 'Te gustaría saber más sobre...' o 'Claro, el saldo inicial es importante...'\n"
            "🔴 CRÍTICO: Si el texto original es una pregunta específica (como '¿Cuál es el saldo inicial para Bancolombia?'), NO agregues explicaciones adicionales\n"
            "RESPONDE SOLO CON JSON PURO. NO INCLUYAS COMENTARIOS.\n"
        )
        prompt += f"Texto a formatear: {texto}\n"

        with get_openai_callback() as cb:
            try:
                response = self.llm.invoke(prompt)
                json_response = response.content.strip()
                
                json_response = re.sub(r'^```json\s*', '', json_response)
                json_response = re.sub(r'\s*```$', '', json_response)
                json_response = json_response.strip()
                
                try:
                    parsed_json = json.loads(json_response)
                except json.JSONDecodeError as e:
                    return {
                        "error": f"Error parseando JSON: {str(e)}",
                        "raw_response": json_response,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_tokens": cb.total_tokens,
                        "total_cost": round(cb.total_cost, 6)
                    }
                    
            except OpenAIError as e:
                return {
                    "error": str(e),
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "total_tokens": cb.total_tokens,
                    "total_cost": round(cb.total_cost, 6)
                }

        return {
            "json": parsed_json,
            "raw_response": json_response,
            "prompt_tokens": cb.prompt_tokens,
            "completion_tokens": cb.completion_tokens,
            "total_tokens": cb.total_tokens,
            "total_cost": round(cb.total_cost, 6)
        }

