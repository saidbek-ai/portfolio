import { generateUserImage } from "./utils.js"

const editPhotoInput = document.getElementById("image_input")
const imagePreview = document.getElementById("image_preview")

function changeImageState(imgUrl) {
  const noAvatarFrame = document.getElementById("no-avatar-frame")

  if (!imgUrl) {
    const userInitialsElement = document.getElementById("user-initials")

    console.log(fName, lName)
    const { userInitials, bgColor } = generateUserImage(fName, lName)

    console.log(userInitials, bgColor)

    // setting user initials
    userInitialsElement.textContent = userInitials
    // setting dynamic background color by user initials
    noAvatarFrame.style.backgroundColor = bgColor.hex
    // show initials
    noAvatarFrame.classList.remove("hidden")
    // hide image preview
    imagePreview.classList.add("hidden")
  } else {
    imagePreview.src = imgUrl
    // hide initials
    noAvatarFrame.classList.add("hidden")
    // show image preview
    imagePreview.classList.remove("hidden")
  }
}

editPhotoInput.addEventListener("change", e => {
  const file = e.target.files[0]

  if (file && file.type.startsWith("image/")) {
    userImageUrl = URL.createObjectURL(file)
  } else {
    //throwing error throw notyf toast
    window.toast.open({ type: "error", text: "Please select a valid image file." })
  }

  // image rendering after new image selection
  changeImageState(userImageUrl)
})

// for initial image rendering
changeImageState(userImageUrl.trim())
