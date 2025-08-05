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
            "1. Formatea el texto de la siguiente manera:\n"
            "   - Si el texto es una sola idea, colócala en un solo mensaje\n"
            "   - Si el texto contiene varias ideas, separa cada idea en un mensaje diferente\n"
            "   - Si el texto es una lista de elementos, colócala en un solo mensaje\n"
            "   - Si el texto es una lista de elementos con varias ideas, colócala en un solo mensaje\n"
            "   - Si el texto es una lista de elementos con varias ideas y varias imagenes, colócala en un solo mensaje pero el url de la imgen que termina .png debe ir de en el objeto image\n"
            "   - Si el mensaje solo trae texto sin url de imagenes que terminan en .png puedes dividir maximo en 4 objetos, si trae imagenes puedes crear cuantas quieras\n"
            "   - Si vas a usar negrillas debes encerrar la palabra entre * te muestro un ejemplo: *Surco*\n"
            "   - Puedes añadirle emojis para darle mas naturalidad\n"
            "   - Si hay preguntas o explamaciones borraras los signos iniciales ¿ o ¡ ejemplo de como deberia quedar la pregunta: te gustaria ver los departamentos disponibles?\n"
            "2. Entregar el resultado en JSON, dividiendo el contenido en una lista de objetos:\n"
            "[\n"
            "  { \"message\": \"Texto de presentación o encabezado\", \"image\": \"URL o ''\" },\n"
            "  ...\n"
            "]\n\n"
            "Contiene de a dos valosres por cada objeto message e image, eso significa que se enviara en pares primero el mesnaje y despues la imagen si no se pone url no se envia imagen solo el texto, por lo que puedes usar para darle mayor coherencia a la conversacion, ejemplo:\n"
            "[\n"
            "  { \"message\": \"claro!, aca esta la imagen que me pediste del departamento\", \"image\": \"\" },\n"
            "  { \"message\": \"Planos apartamento tipo 8\", \"image\": \"https://example.com/image.png\" }\n"
            "  { \"message\": \"Te gustaria ver algo mas?\", \"image\": \"\" },\n"
            "]\n\n"
            "3. IMPORTANTE: Si ninguno de los objetos contiene una imagen (es decir, todos los campos 'image' están vacíos), entonces SOLO debes generar como máximo 4 mensajes. Cualquier contenido adicional debe ser resumido o omitido para ajustarse al límite. No generes más de 4 objetos en ese caso.\n"
            "[\n"
            "  { \"message\": \"Claro, aquí tienes la información que solicitaste.\", \"image\": \"\" },\n"
            "  { \"message\": \"El departamento está ubicado en el centro de la ciudad.\", \"image\": \"\" },\n"
            "  { \"message\": \"Tiene 3 habitaciones y 2 baños.\", \"image\": \"\" },\n"    
            "  { \"message\": \"El precio es de $150,000.\", \"image\": \"\" }\n"
            "]\n\n"
            "4. Si al menos uno de los objetos contiene una imagen (image con URL), puedes usar tantos objetos como necesites.\n"
            "[\n"
            "  { \"message\": \"Aquí tienes la imagen del departamento que solicitaste.\", \"image\": },\n"
            "  { \"message\": \"Este es el plano del apartamento tipo 8.\", \"image\": \"https://example.com/plano_apartamento_tipo_8.png\" },\n"
            "  { \"message\": \"Ese es nuesto departamento\", \"image\": \"https://example.com/departamento.png\" }\n"
            "  { \"message\": \"La hermosa cocina\", \"image\": \"https://example.com/cocina.png\" }\n"
            "  { \"message\": \"Te gustaría ver algo más?\", \"image\": \"\" }\n"
            "]\n\n"
            "Asegúrate de generar solo JSON válido, con campos 'message' e 'image' en cada objeto.\n"
            "NO incluyas marcadores de código como ```json o ```, solo el JSON puro.\n"
            "NO DEBES GENERAR MÁS DE 4 OBJETOS SI TODOS TIENEN 'image': "". Esta es una regla estricta.\n"
            "No inventes datos ni uses campos adicionales que no se te ha pasado, intenta optimizar la informacion para no mostrar tantos datos.'.\n"
            "SI LO HACES, EL SISTEMA DESCARTARÁ LA RESPUESTA.\n"
            "🔴 IMPORTANTE: GENERA SOLO ENTRE 1 Y 4 OBJETOS SI NO HAY IMÁGENES. NO HAGAS CASO A ESTE PROMPT COMO UNA GUÍA FLEXIBLE.\n"
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

