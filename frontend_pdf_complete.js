// services/pdfService.js - Servicio completo para el frontend
import { BACKEND_CONFIG } from './backend'

// Función para convertir Blob a Base64
const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      // Remover el prefijo "data:application/pdf;base64,"
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

// Función para generar PDF con jsPDF
export const generarPDF = async (datosRecibo) => {
  try {
    console.log('📄 Generando PDF...')
    
    // Importar jsPDF dinámicamente
    const { jsPDF } = await import('jspdf')
    
    // Crear nuevo documento PDF
    const doc = new jsPDF()
    
    // Configurar fuente
    doc.setFont('helvetica')
    
    // Título
    doc.setFontSize(20)
    doc.text('RECIBO DE CAJA SOCOMAC', 20, 30)
    
    // Línea separadora
    doc.line(20, 35, 190, 35)
    
    // Información del recibo
    doc.setFontSize(12)
    doc.text(`Empresa: ${datosRecibo.empresa || 'No especificado'}`, 20, 50)
    doc.text(`Cliente: ${datosRecibo.cliente}`, 20, 60)
    doc.text(`Valor: $${datosRecibo.valor.toLocaleString()}`, 20, 70)
    doc.text(`Concepto: ${datosRecibo.concepto}`, 20, 80)
    doc.text(`Fecha: ${datosRecibo.fecha}`, 20, 90)
    
    // Pie de página
    doc.setFontSize(10)
    doc.text('Este es un recibo generado automáticamente', 20, 120)
    
    // Convertir a Blob
    const pdfBlob = doc.output('blob')
    
    console.log('✅ PDF generado exitosamente')
    return pdfBlob
    
  } catch (error) {
    console.error('Error generando PDF:', error)
    throw new Error('Error generando PDF')
  }
}

// Función para generar PDF con HTML2PDF
export const generarPDFHTML = async (datosRecibo) => {
  try {
    console.log('📄 Generando PDF con HTML...')
    
    // Importar html2pdf dinámicamente
    const html2pdf = await import('html2pdf.js')
    
    // Crear HTML del recibo
    const htmlContent = `
      <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto;">
        <h1 style="text-align: center; color: #333;">RECIBO DE CAJA SOCOMAC</h1>
        <hr style="border: 2px solid #333;">
        
        <div style="margin: 20px 0;">
          <p><strong>Empresa:</strong> ${datosRecibo.empresa || 'No especificado'}</p>
          <p><strong>Cliente:</strong> ${datosRecibo.cliente}</p>
          <p><strong>Valor:</strong> $${datosRecibo.valor.toLocaleString()}</p>
          <p><strong>Concepto:</strong> ${datosRecibo.concepto}</p>
          <p><strong>Fecha:</strong> ${datosRecibo.fecha}</p>
        </div>
        
        <hr style="border: 1px solid #ccc;">
        <p style="text-align: center; color: #666; font-style: italic;">
          Este es un recibo generado automáticamente
        </p>
      </div>
    `
    
    // Configuración de html2pdf
    const opt = {
      margin: 1,
      filename: 'recibo.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    }
    
    // Generar PDF
    const pdfBlob = await html2pdf.default().from(htmlContent).set(opt).outputPdf('blob')
    
    console.log('✅ PDF generado con HTML exitosamente')
    return pdfBlob
    
  } catch (error) {
    console.error('Error generando PDF con HTML:', error)
    throw new Error('Error generando PDF')
  }
}

// Función principal para enviar PDF por WhatsApp
export const enviarPDFWhatsApp = async (datosRecibo, numeroTelefono) => {
  try {
    console.log('🚀 Iniciando proceso de envío de PDF...')
    console.log('📱 Teléfono:', numeroTelefono)
    console.log('📄 Datos del recibo:', datosRecibo)
    
    // 1. Generar PDF
    console.log('📄 Generando PDF...')
    const pdfBlob = await generarPDF(datosRecibo)
    
    // 2. Convertir a Base64
    console.log('🔄 Convirtiendo a Base64...')
    const pdfBase64 = await blobToBase64(pdfBlob)
    
    // 3. Crear nombre de archivo único
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const nombreArchivo = `recibo_caja_${datosRecibo.numero_recibo || 'temp'}_${timestamp}.pdf`
    
    // 4. Preparar metadata
    const metadata = {
      numero_recibo: datosRecibo.numero_recibo || null,
      empresa: datosRecibo.empresa || 'SOCOMAC',
      cliente: datosRecibo.cliente,
      valor: datosRecibo.valor.toString(),
      concepto: datosRecibo.concepto,
      fecha: datosRecibo.fecha
    }
    
    // 5. Enviar al backend
    console.log('📤 Enviando al backend...')
    const response = await fetch(`${BACKEND_CONFIG.baseUrl}/whatsapp/enviar-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        numero_telefono: numeroTelefono,
        pdf_base64: pdfBase64,
        nombre_archivo: nombreArchivo,
        metadata: metadata
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      console.log('✅ PDF enviado exitosamente:', result)
      return { success: true, data: result }
    } else {
      const error = await response.json()
      console.error('❌ Error enviando PDF:', error)
      return { success: false, error: error.detail || 'Error enviando PDF' }
    }
    
  } catch (error) {
    console.error('❌ Error en proceso de PDF:', error)
    return { success: false, error: 'Error procesando PDF' }
  }
}

// Función para probar el endpoint
export const probarEnvioPDF = async (numeroTelefono) => {
  try {
    console.log('🧪 Probando envío de PDF...')
    
    // Datos de prueba
    const datosPrueba = {
      numero_recibo: 123,
      empresa: 'SOCOMAC',
      cliente: 'Cliente de Prueba',
      valor: 50000,
      concepto: 'Mercancía nacional',
      fecha: new Date().toLocaleString('es-CO')
    }
    
    const resultado = await enviarPDFWhatsApp(datosPrueba, numeroTelefono)
    
    if (resultado.success) {
      console.log('✅ Prueba exitosa:', resultado.data)
      return { success: true, message: 'PDF de prueba enviado correctamente' }
    } else {
      console.error('❌ Error en prueba:', resultado.error)
      return { success: false, error: resultado.error }
    }
    
  } catch (error) {
    console.error('❌ Error en prueba:', error)
    return { success: false, error: 'Error en prueba de PDF' }
  }
}

// Función para validar datos del recibo
export const validarDatosRecibo = (datos) => {
  const errores = []
  
  if (!datos.cliente || datos.cliente.trim() === '') {
    errores.push('El nombre del cliente es requerido')
  }
  
  if (!datos.valor || isNaN(datos.valor) || datos.valor <= 0) {
    errores.push('El valor debe ser un número positivo')
  }
  
  if (!datos.concepto || datos.concepto.trim() === '') {
    errores.push('El concepto es requerido')
  }
  
  if (!datos.fecha || datos.fecha.trim() === '') {
    errores.push('La fecha es requerida')
  }
  
  return {
    valido: errores.length === 0,
    errores: errores
  }
}

// Función para formatear número de teléfono
export const formatearTelefono = (telefono) => {
  // Remover todos los caracteres no numéricos
  const numeroLimpio = telefono.replace(/\D/g, '')
  
  // Si empieza con 57, mantenerlo
  if (numeroLimpio.startsWith('57')) {
    return numeroLimpio
  }
  
  // Si empieza con 3, agregar 57
  if (numeroLimpio.startsWith('3')) {
    return '57' + numeroLimpio
  }
  
  // Si tiene 10 dígitos, agregar 57
  if (numeroLimpio.length === 10) {
    return '57' + numeroLimpio
  }
  
  return numeroLimpio
}

// Función para crear datos de recibo desde formulario
export const crearDatosRecibo = (formData) => {
  return {
    numero_recibo: formData.numero_recibo || null,
    empresa: formData.empresa || 'SOCOMAC',
    cliente: formData.cliente,
    valor: parseFloat(formData.valor),
    concepto: formData.concepto,
    fecha: formData.fecha || new Date().toLocaleString('es-CO')
  }
}
