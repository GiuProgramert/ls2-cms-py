const canDraggValues = {
  draft: window.isAdmin || window.isAutor,
  revision: window.isAdmin || window.isEditor,
  edited: window.isAdmin || window.isPublisher || window.isEditor,
  published: window.isAdmin || window.isPublisher,
  inactive: false,
};

const defaultCanDrag = false;

/**
 * Obtiene el valor de una cookie
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Cambia el estado de un artículo
 * @param {number} articleId Id del artículo
 * @param {string} articleNewState Nuevo estado del artículo
 * @returns {Promise<Response>}
 * @throws {Error}
 */
async function changeState(articleId, articleNewState) {
  const response = await fetch(
    `/article/${articleId}/update/state/${articleNewState}`,
    {
      method: "GET",
    }
  );

  if (!response.ok) {
    throw new Error("Error updating article state");
  }

  return response;
}

/**
 * Envia un mensaje a un artículo
 * @param {number} articleId Id del artículo
 * @param {string} message Mensaje a enviar
 * @returns {Promise<Response>}
 * @throws {Error}
 */
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

function showSuccessToast(text) {
  window
    .Toastify({
      text,
      position: "center",
      close: true,
      className: "toast",
      style: {
        background: "#0f9d58",
      },
    })
    .showToast();
}

function showErrorToast(text) {
  window
    .Toastify({
      text,
      position: "center",
      close: true,
      className: "toast",
      style: {
        background: "#b90f29",
      },
    })
    .showToast();
}

function showModal(modal) {
  modal.style.display = "block";
}

function closeModal(modal) {
  modal.style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
  const states = document.querySelectorAll(".state");
  const items = document.querySelectorAll(".item");

  const modalMessage = document.getElementById("modalMessage");
  const closeBtnMessage = document.getElementById("closeModal");
  const sendMessageBtn = document.getElementById("send");
  const dontSendMessageBtn = document.getElementById("dontSend");
  const messageInput = document.getElementById("message");

  const modalConfirmation = document.getElementById("modalConfirmation");
  const closeBtnConfirmation = document.getElementById(
    "closeModalConfirmation"
  );
  const confirmBtn = document.getElementById("confirm");
  const dontConfirmBtn = document.getElementById("dontConfirm");

  let draggedItem = null;
  let firstState = null;
  let firstItemContainer = null;
  let lastArticleToSend = null;

  let itemsContainer = null;
  let articleId = null;
  let articleNewState = null;

  // Add draggable attribute to items
  items.forEach((item) => {
    item.addEventListener("dragstart", () => {
      draggedItem = item;
      firstState = item.parentElement.getAttribute("data-state");
      firstItemContainer = item.parentElement;
      item.classList.add("dragging");
    });

    item.addEventListener("dragend", () => item.classList.remove("dragging"));
  });

  // Add event listeners to states
  states.forEach((state) => {
    // Prevent default behavior
    state.addEventListener("dragover", (e) => e.preventDefault());

    // Save the necessary data to change the state of the article
    state.addEventListener("drop", async (e) => {
      e.preventDefault();

      if (draggedItem) {
        itemsContainer = state.querySelector(".items");

        articleId = draggedItem.getAttribute("data-id");
        articleNewState = itemsContainer.getAttribute("data-state");

        itemsContainer.appendChild(draggedItem);

        if (firstState !== articleNewState) showModal(modalConfirmation);
      }
    });
  });

  // To close modal when click on close button
  closeBtnMessage.addEventListener("click", () => closeModal(modalMessage));

  closeBtnConfirmation.addEventListener("click", () => {
    itemsContainer.removeChild(draggedItem);
    firstItemContainer.appendChild(draggedItem);
    closeModal(modalConfirmation);
  });

  sendMessageBtn.addEventListener("click", () => {
    sendMessage(lastArticleToSend, messageInput.value)
      .then(() => showSuccessToast("Mensaje enviado correctamente"))
      .catch(() => showErrorToast("Error al enviar el mensaje"))
      .finally(() => {
        lastArticleToSend = null;
        closeModal(modalMessage);
      });
  });

  confirmBtn.addEventListener("click", () => {
    // If the article is in revision state and the new state is draft, show modal to send message
    if (firstState === "revision" && articleNewState === "draft") {
      lastArticleToSend = articleId;
      showModal(modalMessage);
    }

    if (firstState === articleNewState) return;

    changeState(articleId, articleNewState)
      .then(() => {
        const canDrag = canDraggValues[articleNewState] || defaultCanDrag;
        draggedItem.setAttribute("draggable", canDrag ? "true" : "false");
        showSuccessToast("Estado del artículo actualizado correctamente");
      })
      .catch(() => {
        itemsContainer.removeChild(draggedItem);
        firstItemContainer.appendChild(draggedItem);
        showErrorToast("No puedes modificar el estado de este artículo");
      })
      .finally(() => {
        draggedItem = null;
        firstState = null;
        firstItemContainer = null;
      });

    closeModal(modalConfirmation);
  });

  dontConfirmBtn.addEventListener("click", () => {
    itemsContainer.removeChild(draggedItem);
    firstItemContainer.appendChild(draggedItem);
    closeModal(modalConfirmation);
  });

  dontSendMessageBtn.addEventListener("click", () => closeModal(modalMessage));
});
