import cv2
import tkinter as tk
from tkinter import ttk



import numpy as np

from sklearn.cluster import KMeans
from collections import Counter
import imutils
import pprint
from matplotlib import pyplot as plt
import tkinter.messagebox as messagebox





def extractSkin(image):
    # Taking a copy of the image
    img = image.copy()
    # Converting from BGR Colours Space to HSV
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Defining HSV Threadholds
    lower_threshold = np.array([0, 48, 80], dtype=np.uint8)
    upper_threshold = np.array([20, 255, 255], dtype=np.uint8)

    # Single Channel mask,denoting presence of colours in the about threshold
    skinMask = cv2.inRange(img, lower_threshold, upper_threshold)

    # Cleaning up mask using Gaussian Filter
    skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)

    # Extracting skin from the threshold mask
    skin = cv2.bitwise_and(img, img, mask=skinMask)

    # Return the Skin image
    return cv2.cvtColor(skin, cv2.COLOR_HSV2BGR)


def removeBlack(estimator_labels, estimator_cluster):

    # Check for black
    hasBlack = False

    # Get the total number of occurance for each color
    occurance_counter = Counter(estimator_labels)

    # Quick lambda function to compare to lists
    def compare(x, y): return Counter(x) == Counter(y)

    # Loop through the most common occuring color
    for x in occurance_counter.most_common(len(estimator_cluster)):

        # Quick List comprehension to convert each of RBG Numbers to int
        color = [int(i) for i in estimator_cluster[x[0]].tolist()]

        # Check if the color is [0,0,0] that if it is black
        if compare(color, [0, 0, 0]) == True:
            # delete the occurance
            del occurance_counter[x[0]]
            # remove the cluster
            hasBlack = True
            estimator_cluster = np.delete(estimator_cluster, x[0], 0)
            break

    return (occurance_counter, estimator_cluster, hasBlack)


def getColorInformation(estimator_labels, estimator_cluster, hasThresholding=False):

    # Variable to keep count of the occurance of each color predicted
    occurance_counter = None

    # Output list variable to return
    colorInformation = []

    # Check for Black
    hasBlack = False

    # If a mask has be applied, remove th black
    if hasThresholding == True:

        (occurance, cluster, black) = removeBlack(
            estimator_labels, estimator_cluster)
        occurance_counter = occurance
        estimator_cluster = cluster
        hasBlack = black

    else:
        occurance_counter = Counter(estimator_labels)

    # Get the total sum of all the predicted occurances
    totalOccurance = sum(occurance_counter.values())

    # Loop through all the predicted colors
    for x in occurance_counter.most_common(len(estimator_cluster)):

        index = (int(x[0]))

        # Quick fix for index out of bound when there is no threshold
        index = (index-1) if ((hasThresholding & hasBlack)
                              & (int(index) != 0)) else index

        # Get the color number into a list
        color = estimator_cluster[index].tolist()

        # Get the percentage of each color
        color_percentage = (x[1]/totalOccurance)

        # make the dictionay of the information
        colorInfo = {"cluster_index": index, "color": color,
                     "color_percentage": color_percentage}

        # Add the dictionary to the list
        colorInformation.append(colorInfo)

    return colorInformation


def extractDominantColor(image, number_of_colors=5, hasThresholding=False):

    # Quick Fix Increase cluster counter to neglect the black(Read Article)
    if hasThresholding == True:
        number_of_colors += 1

    # Taking Copy of the image
    img = image.copy()

    # Convert Image into RGB Colours Space
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Reshape Image
    img = img.reshape((img.shape[0]*img.shape[1]), 3)

    # Initiate KMeans Object
    estimator = KMeans(n_clusters=number_of_colors, random_state=0)

    # Fit the image
    estimator.fit(img)

    # Get Colour Information
    colorInformation = getColorInformation(
        estimator.labels_, estimator.cluster_centers_, hasThresholding)
    return colorInformation


def plotColorBar(colorInformation):
    # Create a 500x100 black image
    color_bar = np.zeros((100, 500, 3), dtype="uint8")

    top_x = 0
    for x in colorInformation:
        bottom_x = top_x + (x["color_percentage"] * color_bar.shape[1])

        color = tuple(map(int, (x['color'])))

        cv2.rectangle(color_bar, (int(top_x), 0),
                      (int(bottom_x), color_bar.shape[0]), color, -1)
        top_x = bottom_x
    return color_bar


"""## Section Two.4.2 : Putting it All together: Pretty Print

The function makes print out the color information in a readable manner
"""


def prety_print_data(color_info):
    for x in color_info:
        print(pprint.pformat(x))
        print()


"""
The below lines of code, is the implementation of the above defined function.
"""

'''
Skin Image Primary : https://raw.githubusercontent.com/octalpixel/Skin-Extraction-from-Image-and-Finding-Dominant-Color/master/82764696-open-palm-hand-gesture-of-male-hand_image_from_123rf.com.jpg
Skin Image One     : https://raw.githubusercontent.com/octalpixel/Skin-Extraction-from-Image-and-Finding-Dominant-Color/master/skin.jpg
Skin Image Two     : https://raw.githubusercontent.com/octalpixel/Skin-Extraction-from-Image-and-Finding-Dominant-Color/master/skin_2.jpg
Skin Image Three   : https://raw.githubusercontent.com/octalpixel/Skin-Extraction-from-Image-and-Finding-Dominant-Color/master/Human-Hands-Front-Back-Image-From-Wikipedia.jpg

'''

def get_brightness(color):
    return sum(color) / 3  # Simple average of RGB values



def start_camera():
    global cap
    cap = cv2.VideoCapture(0)
    show_frame()

def show_frame():
    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        raise Exception("Failed to capture frame")

    # Convert the frame to RGB for displaying with Tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    photo = tk.PhotoImage(data=cv2.imencode('.png', frame_rgb)[1].tostring())

    # Update the label with the new frame
    label.config(image=photo)
    label.image = photo

    # Repeat the process by scheduling the function call after a delay (in milliseconds)
    root.after(10, show_frame)

def take_photo():
    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        raise Exception("Failed to capture frame")

    # Save the frame as an image file
    cv2.imwrite('photo.jpg', frame)

    # Load the image
    image_path = 'photo.jpg'  # Replace with your image path
    image = cv2.imread(image_path)
    # Resize image to a width of 250
    image = imutils.resize(image, width=250)

    # Show image
    plt.subplot(3, 1, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("Original Image")
    # plt.show()

    # Apply Skin Mask
    skin = extractSkin(image)

    plt.subplot(3, 1, 2)
    plt.imshow(cv2.cvtColor(skin, cv2.COLOR_BGR2RGB))
    plt.title("Thresholded  Image")
    # plt.show()

    # Find the dominant color. Default is 1 , pass the parameter 'number_of_colors=N' where N is the specified number of colors
    dominantColors = extractDominantColor(skin, hasThresholding=True)

    # Show in the dominant color information
    print("Color Information")
    #颜色 color send 去大预言模型来处理
    prety_print_data(dominantColors)

    # Calculate the brightness for each cluster
    brightness_values = [get_brightness(cluster['color']) for cluster in dominantColors]

    # Count the number of clusters that are considered brighter (brightness > 128)
    brighter_count = sum(1 for brightness in brightness_values if brightness > 128)

    # Count the number of clusters that are considered darker (brightness <= 128)
    darker_count = len(dominantColors) - brighter_count

    if brighter_count > darker_count:
        messagebox.showinfo("Brightness Info", "There is a higher frequency of brighter colors.")
    elif brighter_count < darker_count:
        messagebox.showinfo("Brightness Info", "There is a higher frequency of darker colors.")
    else:
        messagebox.showinfo("Brightness Info", "The frequencies of brighter and darker colors are equal.")


    # Show in the dominant color as bar
    print("Color Bar")
    colour_bar = plotColorBar(dominantColors)
    plt.subplot(3, 1, 3)
    plt.axis("off")
    plt.imshow(colour_bar)
    plt.title("Color Bar")

    plt.tight_layout()
    plt.show()


def stop_camera():
    cap.release()
    label.config(image=None)

# Create a GUI window
root = tk.Tk()
root.title("Take Photo")

# Create a label to display the camera feed
label = ttk.Label(root)
label.pack(pady=10)

# Create buttons to start, stop, and take a photo
start_button = ttk.Button(root, text="Start Camera", command=start_camera)
start_button.pack(side=tk.LEFT, padx=5)
stop_button = ttk.Button(root, text="Stop Camera", command=stop_camera)
stop_button.pack(side=tk.LEFT, padx=5)
photo_button = ttk.Button(root, text="Take Photo", command=take_photo)
photo_button.pack(side=tk.LEFT, padx=5)

# Run the GUI main loop
root.mainloop()
