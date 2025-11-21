# We use tkinter for GUI, PIL for image processing, and struct for packing/unpacking binary data (for header)
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import struct
import math

# Embed function, converts images to RGB
def embed_watermark(host_path, secret_path, output_path):
    try:
        host_img = Image.open(host_path).convert('RGB')
        secret_img = Image.open(secret_path).convert('RGB')

        secret_w, secret_h = secret_img.size
        secret_pixels = list(secret_img.getdata())

        # Storing the secret img size using 'struct.pack'
        # As we need to remember the size of the secret image to rebuild it later
        # '>II' means big-endian, two unsigned integers 
        # 32 bits each = 64 bits total -> 8 bytes (4 for width, 4 for height)
        header = struct.pack('>II', secret_w, secret_h)

        # Convert secret pixels to bytes
        pixels_bytes = b''
        for pixel in secret_pixels:
            pixels_bytes += bytes(pixel)

        # Final data we need to hide: [header] + [all secret pixel bytes]
        data_to_hide = header + pixels_bytes

        # Capacity calculation & checks
        total_bits_needed = len(data_to_hide) * 8
        total_bits_available = host_img.width * host_img.height * 3
        
        # Check if the secret data fits in the host image's LSBs
        if total_bits_needed > total_bits_available:
            # Calculate scale factor
            bits_for_pixels = total_bits_available - 64  # Subtracting 64 bits for the header
            
            # Check for absolute host size limit 
            # Check if the host is too small to fit the minimum data (width * height * 3 < 88 bits)
            # and prevents partial, corrupted embedding.
            if bits_for_pixels < 24: # Need at least 24 bits (3 bytes) for one 1x1 pixel payload
                 messagebox.showerror(
                    "Fatal Error: Host Too Small",
                    f"The host image capacity is only {total_bits_available} bits. "
                    f"A minimum of 88 bits (header + 1 pixel) is required for embedding."
                )
                 return # Stop execution
            
            max_pixels = bits_for_pixels // (3 * 8) # Each pixel needs 3 bytes (24 bits)

            # Calculate new dimensions while maintaining aspect ratio
            scale = math.sqrt(max_pixels / (secret_w * secret_h))
            new_w = max(1, int(secret_w * scale))
            new_h = max(1, int(secret_h * scale))

            # Warning message for the user 
            messagebox.showwarning(
                "Warning: Secret Image Too Large",
                f"The secret image ({secret_w}x{secret_h}) is too large for the host image.\n"
                f"It will be resized to {new_w}x{new_h} to fit."
            )
            
            # Resize and recalculate data
            secret_img = secret_img.resize((new_w, new_h), Image.LANCZOS) # High quality resample
            secret_w, secret_h = new_w, new_h
            secret_pixels = list(secret_img.getdata())

            # Recalculate data_to_hide with resized image
            header = struct.pack('>II', secret_w, secret_h)
            pixels_bytes = b''
            for pixel in secret_pixels:
                pixels_bytes += bytes(pixel)
            data_to_hide = header + pixels_bytes
            total_bits_needed = len(data_to_hide) * 8

        # Post-scaling / Final Capacity Check 
        if total_bits_needed > total_bits_available:
             messagebox.showerror(
                "Fatal Error: Host Too Small",
                f"The host image is too small to embed the secret data. "
                f"Available capacity: {total_bits_available} bits, but {total_bits_needed} bits are required."
            )
             return # Stop execution

        # Convert data (header + pixels) to a binary bit stream
        bit_stream = ''.join(format(byte, '08b') for byte in data_to_hide)

        bit_index = 0
        host_pixels = list(host_img.getdata())
        new_pixels = []

        # LSB Embedding loop
        for pixel in host_pixels:
            r, g, b = pixel
            
            # Embed one bit into the LSB of R
            if bit_index < len(bit_stream):
                bit = int(bit_stream[bit_index])
                bit_index += 1
                r = (r & 0xFE) | bit
                
            # Embed one bit into the LSB of G
            if bit_index < len(bit_stream):
                bit = int(bit_stream[bit_index])
                bit_index += 1
                g = (g & 0xFE) | bit
                
            # Embed one bit into the LSB of B
            if bit_index < len(bit_stream):
                bit = int(bit_stream[bit_index])
                bit_index += 1
                b = (b & 0xFE) | bit
                
            new_pixels.append((r, g, b))

        # Save the image
        new_img = Image.new('RGB', host_img.size)
        new_img.putdata(new_pixels)
        new_img.save(output_path)
        messagebox.showinfo("Success", f"Embedding complete.\nModified image saved as:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Error during embedding: {str(e)}")

# Extractor function 
def extract_watermark(modified_path, output_path):
    try:
        modified_img = Image.open(modified_path).convert('RGB')

        # 1. Extract all LSBs into a continuous bit stream
        bit_stream = ''
        for pixel in modified_img.getdata():
            r, g, b = pixel
            bit_stream += str(r & 1)
            bit_stream += str(g & 1)
            bit_stream += str(b & 1)

        if len(bit_stream) < 64:
            raise ValueError("Not enough data to extract the header (minimum 64 bits needed).")

        # 2. Extract and unpack the 64-bit header (width and height)
        header_bits = bit_stream[:64]
        
        # Convert the 64 header bits back into a byte string (8 bytes)
        # This reverses the process of format(byte, '08b')
        header_bytes = bytes([
            int(header_bits[i:i+8], 2) 
            for i in range(0, 64, 8)
        ])

        # Use struct.unpack to correctly read the two unsigned integers
        # And get back the original width and height of the secret image
        width, height = struct.unpack('>II', header_bytes)
        
        pixels_bits = bit_stream[64:]
        pixels_bits_needed = width * height * 24

        if len(pixels_bits) < pixels_bits_needed:
            raise ValueError(f"Not enough data for the secret image. Needed {pixels_bits_needed} bits, found {len(pixels_bits)}.")

        # 3. Reconstruct the pixel data
        pixels_bits = pixels_bits[:pixels_bits_needed]
        
        # Convert the bit stream into a list of byte values (0-255)
        byte_array = [int(pixels_bits[i:i+8], 2) for i in range(0, len(pixels_bits), 8)]

        # 4. Reconstruct the secret image pixels
        secret_pixels = []
        for i in range(0, len(byte_array), 3):
            r = byte_array[i]
            g = byte_array[i+1]
            b = byte_array[i+2]
            secret_pixels.append((r, g, b))

        # 5. Save the image
        secret_img = Image.new('RGB', (width, height))
        secret_img.putdata(secret_pixels)
        secret_img.save(output_path)
        messagebox.showinfo("Success", f"Secret image saved as:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Error during extraction: {str(e)}")

def create_gui():
    root = tk.Tk()
    root.title("Digital Watermarking")
    root.geometry("500x300")

    # Title + instruction label
    title_label = tk.Label(root, text="Digital Watermarking Tool", font=("Arial", 14, "bold"))
    title_label.pack(pady=(15, 5))

    instruction_label = tk.Label(root, text="Choose an action below.", font=("Arial", 10))
    instruction_label.pack(pady=(0, 15))

    # dialogs with step-by-step instructions 

    def embed_dialog():
        # Step 1: choose host image
        instruction_label.config(text="Step 1: Choose the host image.")
        host_path = filedialog.askopenfilename(
            title="Select Host Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.bmp")]
        )
        if not host_path:
            instruction_label.config(text="Embedding cancelled. Choose an action below.")
            return

        # Step 2: choose secret image
        messagebox.showinfo("Step 2",
                            "Host image selected.\n\nNow choose the SECRET image you want to hide.")
        instruction_label.config(text="Step 2: Choose the secret image to hide.")
        secret_path = filedialog.askopenfilename(
            title="Select Secret Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.bmp")]
        )
        if not secret_path:
            instruction_label.config(text="Embedding cancelled. Choose an action below.")
            return

        # Step 3: choose output filename
        messagebox.showinfo("Step 3",
                            "Secret image selected.\n\nNow choose a NAME and LOCATION\nfor the watermarked image.")
        instruction_label.config(text="Step 3: Choose where to save the watermarked image.")
        output_path = filedialog.asksaveasfilename(
            title="Save Watermarked Image",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png")]
        )
        if not output_path:
            instruction_label.config(text="Embedding cancelled. Choose an action below.")
            return

        instruction_label.config(text="Embedding in progress...")
        embed_watermark(host_path, secret_path, output_path)
        instruction_label.config(text="Done. You can embed or extract another image.")

    def extract_dialog():
        # Step 1: choose watermarked image
        instruction_label.config(text="Step 1: Choose the watermarked image.")
        modified_path = filedialog.askopenfilename(
            title="Select Watermarked Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.bmp")]
        )
        if not modified_path:
            instruction_label.config(text="Extraction cancelled. Choose an action below.")
            return

        # Step 2: choose where to save extracted image
        messagebox.showinfo("Step 2",
                            "Watermarked image selected.\n\nNow choose a NAME and LOCATION\nfor the extracted secret image.")
        instruction_label.config(text="Step 2: Choose where to save the extracted image.")
        output_path = filedialog.asksaveasfilename(
            title="Save Extracted Image",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png")]
        )
        if not output_path:
            instruction_label.config(text="Extraction cancelled. Choose an action below.")
            return

        instruction_label.config(text="Extracting secret image...")
        extract_watermark(modified_path, output_path)
        instruction_label.config(text="Done. You can embed or extract another image.")

    # ----- buttons -----
    tk.Button(
        root,
        text="Embed secret image into host image",
        command=embed_dialog,
        width=40
    ).pack(pady=5)

    tk.Button(
        root,
        text="Extract secret image from watermarked image",
        command=extract_dialog,
        width=40
    ).pack(pady=5)

    # -------------------

    root.mainloop()

if __name__ == "__main__":
    create_gui()
