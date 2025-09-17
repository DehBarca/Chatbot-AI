// Utility function for showing user-friendly error messages
function showError(message, isAlert = true) {
  console.error("Error:", message);
  if (isAlert) {
    alert(`❌ Error: ${message}`);
  }
}

// Utility function for safe DOM element selection
function safeGetElement(id, required = true) {
  try {
    const element = document.getElementById(id);
    if (!element && required) {
      throw new Error(`Element with ID '${id}' not found`);
    }
    return element;
  } catch (error) {
    showError(`No se pudo encontrar el elemento: ${id}`);
    return null;
  }
}

// Initialize the application
document.addEventListener("DOMContentLoaded", async function () {
  try {
    console.log("🚀 Inicializando aplicación...");

    // Load models and files in parallel
    await Promise.allSettled([loadModels(), loadFiles()]);

    // Setup event listeners
    const userInput = safeGetElement("userInput");
    if (userInput) {
      userInput.addEventListener("keydown", function (event) {
        try {
          if (event.key === "Enter") {
            event.preventDefault(); // Prevent form submission
            sendMessage();
          }
        } catch (error) {
          showError(`Error en el evento de teclado: ${error.message}`);
        }
      });
    }

    console.log("✅ Aplicación inicializada correctamente");
  } catch (error) {
    showError(`Error crítico en la inicialización: ${error.message}`);
  }
});

// Load models with comprehensive error handling
async function loadModels() {
  try {
    const response = await fetch("/modelos/");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const models = await response.json();

    if (!Array.isArray(models)) {
      throw new Error("La respuesta del servidor no es válida");
    }

    const select = safeGetElement("modelSelect");
    if (!select) return;

    // Clear existing options
    select.innerHTML = "";

    const groupedModels = {};

    models.forEach((model, index) => {
      try {
        if (!model || typeof model !== "object") {
          console.warn(`Modelo inválido en índice ${index}:`, model);
          return;
        }

        const provider = model.provider || "unknown";
        if (!groupedModels[provider]) {
          groupedModels[provider] = [];
        }
        groupedModels[provider].push(model);
      } catch (error) {
        console.warn(`Error procesando modelo en índice ${index}:`, error);
      }
    });

    Object.keys(groupedModels).forEach((provider) => {
      try {
        const group = document.createElement("optgroup");
        group.label = `${provider} Models`;

        groupedModels[provider].forEach((model) => {
          try {
            const option = document.createElement("option");
            option.value = model.id || "";
            option.textContent = model.nombre || "Modelo sin nombre";
            option.setAttribute("data-provider", provider);
            group.appendChild(option);
          } catch (error) {
            console.warn(`Error creando opción para modelo:`, model, error);
          }
        });

        select.appendChild(group);
      } catch (error) {
        console.warn(`Error creando grupo para proveedor ${provider}:`, error);
      }
    });

    // Set default model
    select.value = "gemini-2.0-flash";

    console.log("✅ Modelos cargados exitosamente");
  } catch (error) {
    showError(`No se pudieron cargar los modelos: ${error.message}`);

    // Fallback: add a default option
    const select = safeGetElement("modelSelect", false);
    if (select) {
      select.innerHTML =
        '<option value="gemini-2.0-flash">Gemini 2.0 Flash (Default)</option>';
    }
  }
}

// Load files with comprehensive error handling
async function loadFiles() {
  try {
    const response = await fetch("/archivos/");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const files = await response.json();

    if (!Array.isArray(files)) {
      throw new Error("La respuesta del servidor no es válida");
    }

    const select = safeGetElement("fileSelect");
    if (!select) return;

    // Clear existing options
    select.innerHTML = "";

    // Add empty option
    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "Seleccionar archivo...";
    select.appendChild(emptyOption);

    files.forEach((file, index) => {
      try {
        if (typeof file !== "string" || !file.trim()) {
          console.warn(`Archivo inválido en índice ${index}:`, file);
          return;
        }

        const option = document.createElement("option");
        option.value = file;
        option.textContent = file;
        select.appendChild(option);
      } catch (error) {
        console.warn(`Error procesando archivo en índice ${index}:`, error);
      }
    });

    select.value = "";
    console.log("✅ Archivos cargados exitosamente");
  } catch (error) {
    showError(`No se pudieron cargar los archivos: ${error.message}`);
  }
}

// Send message with comprehensive error handling
async function sendMessage() {
  let loadingDiv = null;

  try {
    const input = safeGetElement("userInput");
    if (!input) return;

    const text = input.value.trim();
    if (!text) {
      showError("Por favor ingresa un mensaje", false);
      input.focus();
      return;
    }

    // Validate message length
    if (text.length > 4000) {
      showError("El mensaje es demasiado largo (máximo 4000 caracteres)");
      return;
    }

    // Add user message
    if (!addMessage("🕵🏻‍♀️ You", text, "user")) {
      throw new Error("No se pudo agregar el mensaje del usuario");
    }

    input.value = "";

    // Show loading
    loadingDiv = addLoadingMessage();
    if (!loadingDiv) {
      throw new Error("No se pudo mostrar el indicador de carga");
    }

    // Get selected model info
    const select = safeGetElement("modelSelect");
    if (!select || !select.value) {
      throw new Error("Por favor selecciona un modelo");
    }

    const modelId = select.value;
    const modelo =
      select.options[select.selectedIndex]?.textContent || "Modelo desconocido";
    const provider =
      select.options[select.selectedIndex]?.getAttribute("data-provider");

    if (!provider) {
      throw new Error(
        "Proveedor inválido. Por favor selecciona un modelo válido"
      );
    }

    const archivo = safeGetElement("fileSelect")?.value || "";

    // Prepare request data
    const requestData = {
      message: text,
      model: modelId,
      provider: provider,
      archivo: archivo,
    };

    console.log("📤 Enviando mensaje:", requestData);

    // Make API call
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error del servidor (${response.status}): ${errorText}`);
    }

    const data = await response.json();

    if (!data || typeof data !== "object") {
      throw new Error("Respuesta inválida del servidor");
    }

    if (data.error) {
      throw new Error(data.error);
    }

    if (!data.response) {
      throw new Error("El servidor no devolvió una respuesta");
    }

    // Remove loading indicator
    if (loadingDiv) {
      loadingDiv.remove();
      loadingDiv = null;
    }

    // Add bot response
    if (!addMessage("🤖 " + modelo, data.response, "bot")) {
      throw new Error("No se pudo mostrar la respuesta del bot");
    }

    console.log("✅ Mensaje enviado y respuesta recibida exitosamente");
  } catch (error) {
    // Remove loading indicator if it exists
    if (loadingDiv) {
      loadingDiv.remove();
    }

    const errorMessage = error.message || "Error desconocido";
    console.error("❌ Error en sendMessage:", error);

    // Show error to user
    addMessage(
      "🤖 Error",
      `Lo siento, ocurrió un error: ${errorMessage}`,
      "bot error"
    );
    showError(`No se pudo enviar el mensaje: ${errorMessage}`, false);
  }
}

// Add message with error handling
function addMessage(sender, text, type) {
  try {
    if (!sender || !text) {
      throw new Error("Sender y text son requeridos");
    }

    const messagesContainer = safeGetElement("messages");
    if (!messagesContainer) return false;

    const div = document.createElement("div");
    div.classList.add("message", type);

    // Sanitize sender to prevent XSS
    const sanitizedSender = sender.replace(/[<>]/g, "");

    // Only sanitize user messages, allow HTML in bot responses
    let processedText;
    if (type === "user") {
      // Sanitize user input to prevent XSS
      processedText = text.replace(/[<>]/g, (match) =>
        match === "<" ? "&lt;" : "&gt;"
      );
    } else {
      // Allow HTML in bot responses (already processed by server)
      processedText = text;
    }

    div.innerHTML = `<span class="sender">${sanitizedSender}:</span> <span class="text">${processedText}</span>`;

    messagesContainer.appendChild(div);
    div.scrollIntoView({ behavior: "smooth" });

    return true;
  } catch (error) {
    console.error("Error añadiendo mensaje:", error);
    return false;
  }
}

// Add loading message with error handling
function addLoadingMessage() {
  try {
    const messagesContainer = safeGetElement("messages");
    if (!messagesContainer) return null;

    const div = document.createElement("div");
    div.classList.add("message", "loading");
    div.innerHTML =
      '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';

    messagesContainer.appendChild(div);
    div.scrollIntoView({ behavior: "smooth" });

    return div;
  } catch (error) {
    console.error("Error añadiendo mensaje de carga:", error);
    return null;
  }
}

// Reset upload modal with error handling
function resetUploadModal() {
  try {
    const form = safeGetElement("uploadForm", false);
    if (form) {
      form.reset();
    }

    const modalElement = safeGetElement("Archivos", false);
    if (modalElement && typeof bootstrap !== "undefined") {
      const modal = bootstrap.Modal.getInstance(modalElement);
      if (modal) {
        modal.hide();
      }
    }

    console.log("✅ Modal de upload reseteado");
  } catch (error) {
    console.error("Error reseteando modal:", error);
  }
}

// Upload file with comprehensive error handling
async function uploadFile() {
  try {
    const form = safeGetElement("uploadForm");
    const fileInput = safeGetElement("fileInput");

    if (!form || !fileInput) {
      throw new Error("Elementos del formulario no encontrados");
    }

    const files = fileInput.files;
    if (!files || files.length === 0) {
      throw new Error("Por favor selecciona al menos un archivo");
    }

    // Validate file sizes (max 10MB each)
    const maxSize = 10 * 1024 * 1024; // 10MB
    for (let i = 0; i < files.length; i++) {
      if (files[i].size > maxSize) {
        throw new Error(
          `El archivo ${files[i].name} es demasiado grande (máximo 10MB)`
        );
      }
    }

    const formData = new FormData(form);

    console.log("📤 Subiendo archivos...");

    const response = await fetch("/archivos", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error del servidor (${response.status}): ${errorText}`);
    }

    const data = await response.json();

    if (!data || typeof data !== "object") {
      throw new Error("Respuesta inválida del servidor");
    }

    // Show success message
    alert(data.message || "Archivo(s) subido(s) correctamente");

    // Update file dropdown
    await loadFiles();

    // Select the last uploaded file
    const fileSelect = safeGetElement("fileSelect", false);
    if (fileSelect && files.length > 0) {
      const lastUploaded = files[files.length - 1].name;
      fileSelect.value = lastUploaded;
    }

    resetUploadModal();
    console.log("✅ Archivos subidos exitosamente");
  } catch (error) {
    console.error("❌ Error en uploadFile:", error);
    showError(`Error al subir archivo(s): ${error.message}`);
  }
}
