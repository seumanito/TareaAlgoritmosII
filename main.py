
import cohere
from sistema import SistemaArchivos


co = cohere.Client("8u0JnTzSNxLXBrbFwTPIvVuNS11orWR363AN8SqZ") 

def traducir_ia(texto_usuario):
    """
    Recibe: "Por favor crea una carpeta para mis tareas"
    Devuelve: "mkdir Tareas"
    """
    # 1. Instrucciones para que la IA sepa qué hacer (Prompt del Sistema)
    preamble = """
    Eres un traductor de comandos para un sistema operativo simulado.
    Tu trabajo es convertir lenguaje natural a comandos técnicos exactos.
    
    COMANDOS VALIDOS:
    - mkdir <nombre>            (Para crear carpetas)
    - cd <ruta>                 (Para entrar a una carpeta)
    - cd ..                     (Para regresar atrás)
    - type <nombre> "<texto>"   (Para crear archivos con contenido)
    - rmdir /s /q <nombre>      (Para borrar carpetas)
    - dir                       (Para ver el contenido)
    - log                       (Para ver historial)
    - clear log                 (Para borrar historial)
    
    EJEMPLOS:
    Usuario: "Crea una carpeta llamada Fotos" -> Tu respuesta: mkdir Fotos
    Usuario: "Entra a la carpeta Documentos" -> Tu respuesta: cd Documentos
    Usuario: "Regresa" -> Tu respuesta: cd ..
    Usuario: "Qué hay aquí?" -> Tu respuesta: dir
    Usuario: "Crea un archivo Notas.txt que diga Hola" -> Tu respuesta: type Notas.txt "Hola"
    
    Responde ÚNICAMENTE con el comando. No digas "Aquí tienes el comando", ni saludes.
    Si el usuario dice algo que no es una orden (ej: "Hola"), responde: ninguno
    """

    try:
        # 2. Llamada a Cohere
        response = co.chat(
            model="command-r-08-2024", # O el modelo 'command' que te funcione
            message=texto_usuario,
            preamble=preamble,
            temperature=0.0 # Cero creatividad para que sea exacto
        )
        
        # 3. Limpieza de la respuesta
        comando_limpio = response.text.strip()
        
        # Pequeña validación para evitar errores
        if "ninguno" in comando_limpio.lower():
            return None
            
        return comando_limpio

    except Exception as e:
        print(f"Error IA: {e}")
        return None
    pass 

def main():
    sistema = SistemaArchivos()
    print("Sistema iniciado en C:")
    while True:
        entrada = input(f"{sistema.actual.nombre}> ")
        
        if entrada.lower() == "salir":
            break
            
        # 1. INTENTAR TRADUCIR CON IA
        # (Si el usuario escribe un comando directo como "mkdir A", la IA lo devolverá igual, así que sirve para ambos casos)
        comando = traducir_ia(entrada)
        
        if comando is None:
            print("Chatbot: No entendí eso como una orden válida.")
            continue
            
        print(f"🤖 Comando detectado: {comando}") # Para que veas qué hizo la IA
        
        # 2. EJECUTAR EN TU SISTEMA (FASE 2)
        partes = comando.split(" ", 1)
        accion = partes[0].lower()
        argumento = partes[1] if len(partes) > 1 else ""
        
        if accion == "mkdir":
            sistema.mkdir(partes[1])
        elif accion == "cd":
            sistema.cd(partes[1])
        elif accion == "dir":
            sistema.dir()
        elif accion == "log":
            sistema.logs.mostrar_historial()
        elif accion == "salir":
            break

if __name__ == "__main__":
    main()