const button = document.getElementById("open")
const sidebar = document.getElementById("sidebar")
const close = document.getElementById("close")

button.addEventListener("click", () => {
  sidebar.classList.add("show")
})

close.addEventListener("click", () => {
  sidebar.classList.remove("show")
})