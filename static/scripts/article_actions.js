async function sendMessage(articleId, message) {
  const csrftoken = getCookie("csrftoken");


  const formData = new FormData();
  formData.append("articleId", articleId);
  formData.append("message", message);

  const response = await fetch("/kanban/send_message/", {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": csrftoken,
    },
  });

  if (!response.ok) {
    throw new Error("Error sending message");
  }

  return response;
}

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modalMessage");
  const closeBtn = document.getElementById("close");
  const sendMessageBtn = document.getElementById("send");
  const dontSendMessageBtn = document.getElementById("dontSend");
  const messageInput = document.getElementById("message");
  let lastArticleToSend = null;
  let originalHref = null;

  // When the 'Pasar a Borrador' button is clicked
  document
    .querySelector(".detail-link.pasar-borrador")
    .addEventListener("click", function (e) {
      e.preventDefault(); // Prevent default link behavior (navigation)
      const urlParts = this.getAttribute("href").split("/");
      lastArticleToSend = urlParts[2];
      originalHref = this.getAttribute("href"); // Save the original link
      modal.style.display = "block"; // Show modal
    });

  // Close modal when the user clicks on the 'x' button
  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });

  // Close modal when the 'No enviar mensaje' button is clicked
  dontSendMessageBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });

  // Send the message when 'Enviar mensaje' button is clicked
  sendMessageBtn.addEventListener("click", async function () {
    const message = messageInput.value;
    try {
      await sendMessage(lastArticleToSend, message); // Use the sendMessage function
      alert("Mensaje enviado correctamente");
      modal.style.display = "none"; // Close modal after sending

      // Redirect to the original link
      if (originalHref) {
        window.location.href = originalHref;
      }
    } catch (error) {
      alert("Error al enviar el mensaje");
      console.error("Error:", error);
    }
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split("; ");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].split("=");
      if (cookie[0] === name) {
        cookieValue = decodeURIComponent(cookie[1]);
        break;
      }
    }
  }
  return cookieValue;
}
