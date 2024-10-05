const canDraggValues = {
  draft: window.isAdmin || window.isAutor,
  revision: window.isAdmin || window.isEditor,
  edited: window.isAdmin || window.isPublisher || window.isEditor,
  published: window.isAdmin || window.isPublisher,
  inactive: false,
};

const defaultCanDrag = false;

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

document.addEventListener("DOMContentLoaded", () => {
  const states = document.querySelectorAll(".state");
  const items = document.querySelectorAll(".item");

  const modal = document.getElementById("modalMessage");
  const closeBtn = document.getElementsByClassName("close")[0];
  const sendMessageBtn = document.getElementById("send");
  const dontSendMessageBtn = document.getElementById("dontSend");
  const messageInput = document.getElementById("message");

  let draggedItem = null;
  let firstState = null;
  let firstItemContainer = null;
  let lastArticleToSend = null;

  items.forEach((item) => {
    item.addEventListener("dragstart", () => {
      draggedItem = item;
      firstState = item.parentElement.getAttribute("data-state");
      firstItemContainer = item.parentElement;
      item.classList.add("dragging");
    });

    item.addEventListener("dragend", () => {
      item.classList.remove("dragging");
    });
  });

  states.forEach((state) => {
    state.addEventListener("dragover", (e) => {
      e.preventDefault();
    });

    state.addEventListener("drop", async (e) => {
      e.preventDefault();

      if (draggedItem) {
        const itemsContainer = state.querySelector(".items");

        const articleId = draggedItem.getAttribute("data-id");
        const articleNewState = itemsContainer.getAttribute("data-state");

        itemsContainer.appendChild(draggedItem);

        if (firstState === "revision" && articleNewState === "draft") {
          lastArticleToSend = articleId;
          modal.style.display = "block";
        }

        if (firstState !== articleNewState) {
          changeState(articleId, articleNewState)
            .then(() => {
              const canDrag = canDraggValues[articleNewState] || defaultCanDrag;
              draggedItem.setAttribute("draggable", canDrag ? "true" : "false");
            })
            .catch(() => {
              itemsContainer.removeChild(draggedItem);
              firstItemContainer.appendChild(draggedItem);

              window
                .Toastify({
                  text: "No puedes modificar el estado de este artículo",
                  position: "center",
                  close: true,
                  className: "toast",
                  style: {
                    background: "#b90f29",
                  },
                })
                .showToast();
            })
            .finally(() => {
              draggedItem = null;
              firstState = null;
              firstItemContainer = null;
            });
        }
      }
    });
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  sendMessageBtn.addEventListener("click", () => {
    sendMessage(lastArticleToSend, messageInput.value)
      .then(() => {
        window
          .Toastify({
            text: "Mensaje enviado correctamente",
            position: "center",
            close: true,
            className: "toast",
            style: {
              background: "#0f9d58",
            },
          })
          .showToast();
      })
      .catch(() => {
        window
          .Toastify({
            text: "Error al enviar el mensaje",
            position: "center",
            close: true,
            className: "toast",
            style: {
              background: "#b90f29",
            },
          })
          .showToast();
      })
      .finally(() => {
        lastArticleToSend = null;
        modal.style.display = "none";
      });
  });

  dontSendMessageBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });
});
