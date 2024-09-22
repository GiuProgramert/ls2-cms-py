const canDraggValues = {
  draft: window.isAdmin || window.isAutor,
  revision: window.isAdmin || window.isEditor,
  edited: window.isAdmin || window.isPublisher || window.isEditor,
  published: window.isAdmin || window.isPublisher,
  inactive: false,
};

const defaultCanDrag = false;

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

document.addEventListener("DOMContentLoaded", () => {
  const states = document.querySelectorAll(".state");
  const items = document.querySelectorAll(".item");

  let draggedItem = null;
  let firstState = null;

  items.forEach((item) => {
    item.addEventListener("dragstart", () => {
      draggedItem = item;
      firstState = item.parentElement.getAttribute("data-state");
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

        if (firstState !== articleNewState) {
          changeState(articleId, articleNewState).then(() => {
            itemsContainer.appendChild(draggedItem);

            const canDrag = canDraggValues[articleNewState] || defaultCanDrag;
            draggedItem.setAttribute("draggable", canDrag ? "true" : "false");

            draggedItem = null;
            firstState = null;
          }).catch(() => {
            window.Toastify({
              text: "No puedes modificar el estado de este artículo",
              position: "center",
              close: true,
              className: "toast",
              style: {
                background: "#b90f29",
              }
            }).showToast();
          });
        }
      }
    });
  });
});
