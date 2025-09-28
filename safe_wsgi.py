def app(environ, start_response):
    """Una aplicación WSGI segura que siempre funciona."""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    # Devuelve un mensaje simple que nos dice que estamos en "modo mantenimiento"
    message = b"Safe mode enabled. Container is running. Ready for SSH and migrations."
    return [message]