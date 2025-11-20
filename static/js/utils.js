const colorPalette = [
  { hex: "#45a3e5", name: "Blue" },
  { hex: "#f06292", name: "Pink" },
  { hex: "#81c784", name: "Green" },
  { hex: "#ffb74d", name: "Orange" },
  { hex: "#e57373", name: "Red" },
  { hex: "#ba68c8", name: "Purple" },
  { hex: "#4db6ac", name: "Teal" }
]

function getUserInitials(firstName = "", lastName = "") {
  const initials = `${firstName ? firstName[0] : ""}${lastName ? lastName[0] : ""}`
  return initials.toUpperCase()
}

function getUserImageBgColor(fullName = "", colorPalette = []) {
  if (fullName.trim().length === 0) {
    return colorPalette[0]
  }

  let hash = 0

  for (let i = 0; i < fullName.length; i++) {
    hash = fullName.charCodeAt(i) + ((hash << 5) - hash)
  }

  const index = Math.abs(hash % colorPalette.length)

  return colorPalette[index]
}

function generateUserImage(fName, lName) {
  const userInitials = getUserInitials(fName, lName)
  const bgColor = getUserImageBgColor(`${fName ? fName : ""} ${lName ? lName : ""}`, colorPalette)

  return { bgColor, userInitials }
}

export { generateUserImage, getUserInitials }
