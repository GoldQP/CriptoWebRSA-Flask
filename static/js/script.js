document.addEventListener('DOMContentLoaded', () => {
    // Referencias a los elementos del DOM para Cifrado (Emisor)
    const encryptButton = document.getElementById('encryptButton');
    const fileInputEncrypt = document.getElementById('fileInputEncrypt'); // Input de archivo
    const encryptedOutputDisplay = document.getElementById('encryptedOutputDisplay'); // Área de texto para mostrar
    const downloadEncryptedFile = document.getElementById('downloadEncryptedFile'); // Enlace de descarga
    const encryptTableBody = document.querySelector('#encryptTable tbody');

    // Referencias a los elementos del DOM para los detalles de las claves
    const pVal = document.getElementById('p_val');
    const qVal = document.getElementById('q_val');
    const nVal = document.getElementById('n_val');
    const eulerVal = document.getElementById('euler_val');
    const publicNVal = document.getElementById('public_n_val');
    const publicEVal = document.getElementById('public_e_val');
    const privateNVal = document.getElementById('private_n_val');
    const privateDVal = document.getElementById('private_d_val');

    // Referencias a los elementos del DOM para Descifrado (Receptor)
    const decryptButton = document.getElementById('decryptButton');
    const fileInputDecrypt = document.getElementById('fileInputDecrypt'); // Input de archivo
    const decryptedOutput = document.getElementById('decryptedOutput'); // Área de texto para mostrar
    const downloadDecryptedFile = document.getElementById('downloadDecryptedFile'); // Enlace de descarga
    const decryptTableBody = document.querySelector('#decryptTable tbody');

    // --- Lógica de Cifrado (Emisor) ---
    if (encryptButton) {
        encryptButton.addEventListener('click', async () => {
            const file = fileInputEncrypt.files[0]; // Obtiene el primer archivo seleccionado
            if (!file) {
                alert('Por favor, selecciona un archivo de texto (.txt) para cifrar.');
                return;
            }

            const formData = new FormData(); // Usa FormData para enviar archivos
            formData.append('file', file); // 'file' debe coincidir con el nombre esperado en Flask (request.files['file'])

            try {
                const response = await fetch('/api/encrypt_file', {
                    method: 'POST',
                    body: formData, // No Content-Type header; FormData lo establece automáticamente
                });

                const data = await response.json();

                if (response.ok) {
                    // Mostrar contenido en textarea
                    encryptedOutputDisplay.value = data.encrypted_message_base64_display;

                    // Preparar enlace de descarga
                    const blob = new Blob([atob(data.file_content_base64)], { type: 'text/plain' });
                    downloadEncryptedFile.href = URL.createObjectURL(blob);
                    downloadEncryptedFile.style.display = 'block'; // Mostrar el enlace

                    // Mostrar claves
                    pVal.textContent = data.p;
                    qVal.textContent = data.q;
                    nVal.textContent = data.n;
                    eulerVal.textContent = data.euler_phi;
                    publicNVal.textContent = data.public_key.split(',')[0];
                    publicEVal.textContent = data.public_key.split(',')[1];
                    privateNVal.textContent = data.private_key_for_display.split(',')[0];
                    privateDVal.textContent = data.private_key_for_display.split(',')[1];

                    // Mostrar proceso de cifrado
                    encryptTableBody.innerHTML = '';
                    data.char_details.forEach(item => {
                        const row = encryptTableBody.insertRow();
                        row.insertCell(0).textContent = item.char;
                        row.insertCell(1).textContent = item.ascii;
                        row.insertCell(2).textContent = item.encrypted;
                    });

                    alert('Archivo cifrado y listo para descargar!');
                } else {
                    alert('Error al cifrar: ' + (data.error || 'Desconocido'));
                    console.error('Error del servidor:', data);
                }
            } catch (error) {
                console.error('Error al conectar con el servidor de cifrado:', error);
                alert('Hubo un error de conexión al cifrar el archivo. Revisa la consola del navegador (F12) para más detalles.');
            }
        });
    }

    // --- Lógica de Descifrado (Receptor) ---
    if (decryptButton) {
        decryptButton.addEventListener('click', async () => {
            const file = fileInputDecrypt.files[0];
            if (!file) {
                alert('Por favor, selecciona el archivo cifrado (.txt) para descifrar.');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/decrypt_file', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();

                if (response.ok) {
                    // Mostrar mensaje descifrado en textarea
                    decryptedOutput.value = data.decrypted_message_display;

                    // Preparar enlace de descarga
                    const blob = new Blob([atob(data.file_content_base64)], { type: 'text/plain' });
                    downloadDecryptedFile.href = URL.createObjectURL(blob);
                    downloadDecryptedFile.style.display = 'block'; // Mostrar el enlace

                    // Mostrar proceso de descifrado
                    decryptTableBody.innerHTML = '';
                    data.char_details.forEach(item => {
                        const row = decryptTableBody.insertRow();
                        row.insertCell(0).textContent = item.encrypted_val;
                        row.insertCell(1).textContent = item.decrypted_ascii;
                        row.insertCell(2).textContent = item.decrypted_char;
                    });

                    alert('Archivo descifrado y listo para descargar!');
                } else {
                    alert('Error al descifrar: ' + (data.error || 'Desconocido'));
                    console.error('Error del servidor:', data);
                }
            } catch (error) {
                console.error('Error al conectar con el servidor de descifrado:', error);
                alert('Hubo un error de conexión al descifrar el archivo. Revisa la consola del navegador (F12) para más detalles.');
            }
        });
    }

    // Función para resaltar el enlace activo en la navegación (mantenido del anterior)
    document.addEventListener('DOMContentLoaded', () => {
        const navLinks = document.querySelectorAll('nav ul li a');
        const currentPath = window.location.pathname;

        navLinks.forEach(link => {
            // Elimina la lógica de url_for para que funcione directamente en JS
            const linkHref = link.getAttribute('href');

            // Ajuste para la ruta raíz y otras rutas
            if (currentPath === '/' && linkHref === '/') {
                link.classList.add('active');
            } else if (currentPath !== '/' && linkHref !== '/' && currentPath.includes(linkHref)) {
                link.classList.add('active');
            }
        });
    });
});