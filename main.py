
import cohere
from sistema import SistemaArchivos


co = cohere.Client("8u0JnTzSNxLXBrbFwTPIvVuNS11orWR363AN8SqZ") 

def traducir_ia(texto_usuario):

    # Instrucciones
    preamble = """
    Eres un traductor de comandos para un sistema operativo simulado.
    Tu trabajo es convertir lenguaje natural a comandos técnicos exactos.
    
    COMANDOS VALIDOS:
    - mkdir <nombre>            (Para crear carpetas)
    - cd <ruta>                 (Para entrar a una carpeta)
    - cd ..                     (Para regresar atrás)
    - type <nombre> "<texto>"   (Para crear archivos con contenido)
    - rmdir <nombre>            (Para borrar carpetas)
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
    
        response = co.chat(
            model="command-r-08-2024", 
            message=texto_usuario,
            preamble=preamble,
            temperature=0.0 
        )
        
  
        comando_limpio = response.text.strip()
        
        if "ninguno" in comando_limpio.lower():
            return None
            
        return comando_limpio

    except Exception as e:
        print(f"Error IA: {e}")
        return None
    pass 

def main():
    sistema = SistemaArchivos()

    sistema.cargar_sistema()
    print("Consola del Sistema de Archivos Simulado")
    while True:
        entrada = input(f"{sistema.actual.nombre}> ")
        
        if entrada.lower() == "salir":
            break
            

        comando = traducir_ia(entrada)
        
        if comando is None:
            print("Chatbot: No entendí eso como una orden válida.")
            continue
            
        print(f" Comando detectado: {comando}") 
        

        partes = comando.split(" ", 1)
        accion = partes[0].lower()
        argumento = partes[1] if len(partes) > 1 else ""
        
        if accion == "mkdir":
            sistema.mkdir(argumento)
            sistema.guardar_sistema()
        elif accion == "cd":
            sistema.cd(argumento)
        elif accion == "dir":
            sistema.dir()
        elif accion == "type":

            datos_archivo = argumento.split(" ", 1)
            
            nombre_archivo = datos_archivo[0]
            
            if len(datos_archivo) > 1:
                contenido = datos_archivo[1].strip('"') 
            else:
                contenido = "" 

           
            sistema.type(nombre_archivo, contenido)
            sistema.guardar_sistema()
        elif accion == "rmdir":
            sistema.rmdir(argumento)
            sistema.guardar_sistema() 
        elif accion == "clear": 
            sistema.vaciar_logs()

        elif accion == "log":
            sistema.logs.mostrar_historial()
        elif accion == "salir":
            break

if __name__ == "__main__":
    main()