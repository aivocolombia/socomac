// Ejemplo de uso del servicio de PDF
import { 
  enviarPDFWhatsApp, 
  probarEnvioPDF, 
  validarDatosRecibo, 
  formatearTelefono,
  crearDatosRecibo 
} from './services/pdfService'

// Ejemplo 1: Envío básico de PDF
export const ejemploEnvioBasico = async () => {
  try {
    // Datos del recibo
    const datosRecibo = {
      numero_recibo: 123,
      empresa: 'SOCOMAC',
      cliente: 'David Cuellar',
      valor: 10000,
      concepto: 'Mercancía nacional',
      fecha: new Date().toLocaleString('es-CO')
    }
    
    // Número de teléfono (formateado)
    const numeroTelefono = formatearTelefono('3172288329') // Se convierte a 573172288329
    
    // Enviar PDF
    const resultado = await enviarPDFWhatsApp(datosRecibo, numeroTelefono)
    
    if (resultado.success) {
      console.log('✅ PDF enviado exitosamente:', resultado.data)
      return resultado
    } else {
      console.error('❌ Error enviando PDF:', resultado.error)
      return resultado
    }
    
  } catch (error) {
    console.error('❌ Error en ejemplo:', error)
    return { success: false, error: error.message }
  }
}

// Ejemplo 2: Envío desde formulario
export const ejemploDesdeFormulario = async (formData) => {
  try {
    // Validar datos del formulario
    const validacion = validarDatosRecibo(formData)
    
    if (!validacion.valido) {
      return {
        success: false,
        error: 'Datos inválidos',
        detalles: validacion.errores
      }
    }
    
    // Crear datos del recibo
    const datosRecibo = crearDatosRecibo(formData)
    
    // Formatear teléfono
    const numeroTelefono = formatearTelefono(formData.telefono)
    
    // Enviar PDF
    const resultado = await enviarPDFWhatsApp(datosRecibo, numeroTelefono)
    
    return resultado
    
  } catch (error) {
    console.error('❌ Error en formulario:', error)
    return { success: false, error: error.message }
  }
}

// Ejemplo 3: Prueba del sistema
export const ejemploPrueba = async (numeroTelefono) => {
  try {
    console.log('🧪 Iniciando prueba del sistema...')
    
    // Formatear teléfono
    const telefonoFormateado = formatearTelefono(numeroTelefono)
    
    // Ejecutar prueba
    const resultado = await probarEnvioPDF(telefonoFormateado)
    
    return resultado
    
  } catch (error) {
    console.error('❌ Error en prueba:', error)
    return { success: false, error: error.message }
  }
}

// Ejemplo 4: Componente React
export const ComponenteEnvioPDF = () => {
  const [cargando, setCargando] = useState(false)
  const [resultado, setResultado] = useState(null)
  
  const manejarEnvio = async (datosFormulario) => {
    setCargando(true)
    setResultado(null)
    
    try {
      const resultado = await ejemploDesdeFormulario(datosFormulario)
      setResultado(resultado)
    } catch (error) {
      setResultado({ success: false, error: error.message })
    } finally {
      setCargando(false)
    }
  }
  
  return (
    <div>
      <h2>Enviar PDF por WhatsApp</h2>
      
      {cargando && <p>Enviando PDF...</p>}
      
      {resultado && (
        <div>
          {resultado.success ? (
            <div style={{ color: 'green' }}>
              ✅ PDF enviado exitosamente
            </div>
          ) : (
            <div style={{ color: 'red' }}>
              ❌ Error: {resultado.error}
            </div>
          )}
        </div>
      )}
      
      {/* Aquí iría tu formulario */}
    </div>
  )
}

// Ejemplo 5: Función de utilidad para debugging
export const debugPDF = async (datosRecibo, numeroTelefono) => {
  console.log('🔍 Debugging PDF...')
  console.log('Datos del recibo:', datosRecibo)
  console.log('Número de teléfono:', numeroTelefono)
  
  // Validar datos
  const validacion = validarDatosRecibo(datosRecibo)
  console.log('Validación:', validacion)
  
  if (!validacion.valido) {
    console.error('❌ Datos inválidos:', validacion.errores)
    return { success: false, error: 'Datos inválidos', detalles: validacion.errores }
  }
  
  // Formatear teléfono
  const telefonoFormateado = formatearTelefono(numeroTelefono)
  console.log('Teléfono formateado:', telefonoFormateado)
  
  // Intentar envío
  try {
    const resultado = await enviarPDFWhatsApp(datosRecibo, telefonoFormateado)
    console.log('Resultado:', resultado)
    return resultado
  } catch (error) {
    console.error('Error en debug:', error)
    return { success: false, error: error.message }
  }
}

// Ejemplo 6: Manejo de errores específicos
export const manejarErroresPDF = (error) => {
  if (error.includes('CORS')) {
    return 'Error de CORS: Verifica la configuración del backend'
  }
  
  if (error.includes('timeout')) {
    return 'Timeout: El servidor tardó demasiado en responder'
  }
  
  if (error.includes('PDF')) {
    return 'Error de PDF: Verifica que el archivo sea válido'
  }
  
  if (error.includes('telefono')) {
    return 'Error de teléfono: Verifica el formato del número'
  }
  
  return `Error desconocido: ${error}`
}

// Ejemplo 7: Configuración de retry
export const enviarPDFConRetry = async (datosRecibo, numeroTelefono, maxIntentos = 3) => {
  for (let intento = 1; intento <= maxIntentos; intento++) {
    try {
      console.log(`🔄 Intento ${intento}/${maxIntentos}`)
      
      const resultado = await enviarPDFWhatsApp(datosRecibo, numeroTelefono)
      
      if (resultado.success) {
        console.log(`✅ Éxito en intento ${intento}`)
        return resultado
      }
      
      if (intento < maxIntentos) {
        console.log(`⏳ Esperando antes del siguiente intento...`)
        await new Promise(resolve => setTimeout(resolve, 2000 * intento))
      }
      
    } catch (error) {
      console.error(`❌ Error en intento ${intento}:`, error)
      
      if (intento === maxIntentos) {
        return { success: false, error: error.message }
      }
    }
  }
  
  return { success: false, error: 'Máximo de intentos alcanzado' }
}
