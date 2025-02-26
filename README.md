# 📷 Image Steganography in Python

## 🔍 Overview
This project implements **image-based text steganography** using Python and OpenCV. It allows users to **hide a secret message inside an image** and retrieve it later using a passcode.

## ✨ Features
- **Text Encoding:** Hides a secret message inside an image by modifying pixel values.
- **Text Decoding:** Extracts the hidden message from the image if the correct passcode is provided.
- **Passcode Protection:** Ensures that only authorized users can decode the message.
- **Efficient Storage:** Uses the **blue channel** of each pixel to store character ASCII values.

## ⚙️ Requirements
Ensure you have the following installed:

- **Python 3.x**
- **OpenCV (`cv2`)**

To install OpenCV, run:
```sh
pip install opencv-python
```

## 🚀 Usage

### 1️⃣ Encoding (Hiding a Message)
Run the script and enter the secret message along with a passcode:
```sh
python steganography.py
```
- The script loads `mypic.jpg`, hides the message inside it, and saves the result as `encryptedImage.jpg`.
- The modified image will automatically open after encoding.

### 2️⃣ Decoding (Retrieving the Message)
- Run the script again.
- Enter the correct passcode to reveal the hidden message.

## 🔧 Code Explanation
### 📝 **Encoding Process:**
1. Reads the image (`mypic.jpg`).
2. Converts each character of the message into its ASCII value.
3. Stores the values sequentially in the **blue channel** of the image.
4. Saves the modified image as `encryptedImage.jpg`.

### 🔍 **Decoding Process:**
1. Reads the modified image.
2. Extracts ASCII values from the **blue channel**.
3. Converts them back into readable text.
4. Displays the hidden message if the passcode is correct.

## 🔖 Notes
- The image must be large enough to store the entire message.
- A termination character (`~`) is added to mark the end of the message.
- If an incorrect passcode is entered, the message remains hidden.

## 📜 License
This project is **open-source** and available for personal and educational use.

