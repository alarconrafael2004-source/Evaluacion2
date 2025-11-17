function iniciarWebex(destino) {
    // Configuración del widget
    const webexConfig = {
        destination: destino, // Correo de tu compañero
        destinationType: 'email', // o 'sip' si usas SIP URI
        accessibilityFeatures: ['fullScreen', 'joinWithoutVideo'],
    };
    
    // Inicializar el widget
    Webex.init();
    
    // Crear el widget de meeting
    Webex.meetings.createMeetingWidget(webexConfig).then(function(widget) {
        // Unirse a la reunión automáticamente
        widget.join();
        
        // Opcional: Manejar eventos
        widget.on('MEETING_JOINED', function() {
            console.log('Te has unido a la reunión');
        });
        
        widget.on('MEETING_ENDED', function() {
            console.log('La reunión ha terminado');
        });
    }).catch(function(error) {
        console.error('Error al crear el widget:', error);
        alert('Error al iniciar la llamada: ' + error.message);
    });
}
