// services/pdfService.js - Para el frontend
import { createClient } from '@supabase/supabase-js'
import { BACKEND_CONFIG } from './backend'

// Configuración de Supabase
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseKey = process.env.REACT_APP_SUPABASE_ANON_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

// Función para subir PDF a Supabase
export const subirPDFSupabase = async (pdfBlob, nombreArchivo = 'documento.pdf') => {
  try {
    console.log('☁️ Subiendo PDF a Supabase...')
    
    // Generar nombre único
    const timestamp = Date.now()
    const nombreUnico = `${timestamp}_${nombreArchivo}`
    
    // Subir a Supabase Storage
    const { data, error } = await supabase.storage
      .from('pdfs') // Bucket para PDFs
      .upload(nombreUnico, pdfBlob, {
        contentType: 'application/pdf',
        upsert: false
      })
    
    if (error) {
      console.error('Error subiendo PDF:', error)
      return { success: false, error: error.message }
    }
    
    // Obtener URL pública
    const { data: urlData } = supabase.storage
      .from('pdfs')
      .getPublicUrl(nombreUnico)
    
    console.log('✅ PDF subido exitosamente:', urlData.publicUrl)
    
    return {
      success: true,
      url: urlData.publicUrl,
      nombre: nombreUnico
    }
    
  } catch (error) {
    console.error('Error subiendo PDF:', error)
    return { success: false, error: 'Error subiendo archivo' }
  }
}

// Función para enviar documento por WhatsApp
export const enviarDocumentoWhatsApp = async (numeroTelefono, documentoUrl, nombreArchivo, mensaje) => {
  try {
    console.log('📱 Enviando documento por WhatsApp...')
    
    const response = await fetch(`${BACKEND_CONFIG.baseUrl}/whatsapp/enviar-documento-completo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        numero_telefono: numeroTelefono,
        documento_url: documentoUrl,
        nombre_archivo: nombreArchivo,
        mensaje: mensaje
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      console.log('✅ Documento enviado exitosamente:', result)
      return { success: true, data: result }
    } else {
      const error = await response.json()
      console.error('❌ Error enviando documento:', error)
      return { success: false, error: error.detail || 'Error enviando documento' }
    }
    
  } catch (error) {
    console.error('❌ Error enviando documento:', error)
    return { success: false, error: 'Error de conexión' }
  }
}

// Función principal: generar PDF y enviar por WhatsApp
export const generarYEnviarPDF = async (datosRecibo, numeroTelefono) => {
  try {
    console.log('📄 Iniciando proceso de PDF...')
    
    // 1. Generar PDF
    console.log('📄 Generando PDF...')
    const pdfBlob = await generarPDF(datosRecibo)
    
    // 2. Subir a Supabase
    console.log('☁️ Subiendo PDF a Supabase...')
    const uploadResult = await subirPDFSupabase(pdfBlob, 'recibo.pdf')
    
    if (!uploadResult.success) {
      return { success: false, error: uploadResult.error }
    }
    
    // 3. Enviar por WhatsApp
    console.log('📱 Enviando PDF por WhatsApp...')
    const whatsappResult = await enviarDocumentoWhatsApp(
      numeroTelefono,
      uploadResult.url,
      'recibo.pdf',
      'Aquí está su recibo generado'
    )
    
    return whatsappResult
    
  } catch (error) {
    console.error('Error generando y enviando PDF:', error)
    return { success: false, error: 'Error procesando PDF' }
  }
}

// Función para generar PDF (ejemplo con jsPDF)
export const generarPDF = async (datos) => {
  try {
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
    doc.text(`Empresa: ${datos.empresa || 'No especificado'}`, 20, 50)
    doc.text(`Cliente: ${datos.cliente}`, 20, 60)
    doc.text(`Valor: $${datos.valor.toLocaleString()}`, 20, 70)
    doc.text(`Concepto: ${datos.concepto}`, 20, 80)
    doc.text(`Fecha: ${datos.fecha}`, 20, 90)
    
    // Pie de página
    doc.setFontSize(10)
    doc.text('Este es un recibo generado automáticamente', 20, 120)
    
    // Convertir a Blob
    const pdfBlob = doc.output('blob')
    
    return pdfBlob
    
  } catch (error) {
    console.error('Error generando PDF:', error)
    throw new Error('Error generando PDF')
  }
}

// Función alternativa con HTML2PDF
export const generarPDFHTML = async (datos) => {
  try {
    // Importar html2pdf dinámicamente
    const html2pdf = await import('html2pdf.js')
    
    // Crear HTML del recibo
    const htmlContent = `
      <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h1>RECIBO DE CAJA SOCOMAC</h1>
        <hr>
        <p><strong>Empresa:</strong> ${datos.empresa || 'No especificado'}</p>
        <p><strong>Cliente:</strong> ${datos.cliente}</p>
        <p><strong>Valor:</strong> $${datos.valor.toLocaleString()}</p>
        <p><strong>Concepto:</strong> ${datos.concepto}</p>
        <p><strong>Fecha:</strong> ${datos.fecha}</p>
        <hr>
        <p><em>Este es un recibo generado automáticamente</em></p>
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
    
    return pdfBlob
    
  } catch (error) {
    console.error('Error generando PDF con HTML:', error)
    throw new Error('Error generando PDF')
  }
}
