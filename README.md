# 📖 Digital Watermarking Tool (LSB Algorithm)

### Group 19

This project implements a digital watermarking application using the **Least Significant Bit (LSB) steganography algorithm**. The tool is built with Python and utilizes the LSBs of a host image to conceal a secret image.

The application includes robust capacity handling, automatically resizing the secret image if it's too large, or throwing a fatal error if the host image is physically too small to prevent data corruption.

### Note
For instruction on how to utilize the test cases provided, please read the _"Test Cases Explanation.txt"_

---

### ⚙️ Prerequisites (What You Need)

To run this application, you must have **Python 3.x** installed, along with the following libraries:

1.  **Pillow:** Used for all image loading, manipulation, and saving.
2.  **Tkinter:** Used to provide the Graphical User Interface (GUI). (Note: Tkinter is usually included with standard Python installations.)
3.  **Struct:** Used for packing and unpacking binary data (the image header).

### Installation

You can install the required dependency (Pillow) via pip:

```bash
pip install Pillow
```

### ▶️ How to Run the Application

1.  Save the provided Python code (watermark.py).

2.  Open your terminal or command prompt.

3.  Navigate to the directory where you saved the file.

4.  Execute the script using the Python interpreter:

```bash
python watermark.py
```

A desktop GUI window titled "Digital Watermarking" will open.

### 🛠 Usage Instructions
**1. Embedding a Secret Image -**
Click the "Embed secret image into host image" button.

Step 1: Select the Host Image (the carrier). PNG format is recommended.

Step 2: Select the Secret Image (the watermark).

Step 3: Choose the output location and name for the final watermarked image (must be saved as a .png file).

*A Success message will confirm the embedding.*

### Capacity Handling Notes:
- If the secret image is too large, the program will display a Warning and automatically scale the secret image down to fit.

- If the host image is too small to even contain the minimum 88 bits of data, a Fatal Error will be displayed, and the process will stop to prevent file corruption.

**2. Extracting the Secret Image -**
Click the "Extract secret image from watermarked image" button.

Step 1: Select the Watermarked Image (the PNG file containing the hidden data).

Step 2: Choose the output location and name for the extracted secret image.

*A Success message will confirm the extraction, and the original (or scaled) secret image will be saved.*
