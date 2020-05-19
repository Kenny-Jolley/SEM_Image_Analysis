#!/usr/bin/env python

# This Script reads in an image and attempts to detect vertical and horizontal fiducial marks.
# The script picks the two marks either side of the centre of the image.
# It then calculates the distance between the detected marks and annotates this on an output image.
# Caution: the calculated distance assumes the input width is supplied correctly
# todo: Autodetect the image width using pytesseract

# Usage:
# TEM_Image_Analysis_Milled_Line_Detect.py  filename  img_width  crop_top  crop_bottom  crop_left  crop_right

# Imports
import sys
import os
import cv2
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


# Line detector function
def tem_image_analysis_depo_line_detect(**kwargs):
    # Default parameters
    # Can be overridden by supplying keyword args on function call
    # or you can change the default behaviour by modifying the default values here
    verbose = kwargs.get('verbose', False)
    filename = kwargs.get('filename', 'img.tif')
    real_width = kwargs.get('img_width', 10.0)
    # Initial crop params - number of pixels to crop from the edges.
    crop_top = kwargs.get('crop_top', 100)
    crop_bottom = kwargs.get('crop_bottom', 300)
    crop_left = kwargs.get('crop_left', 100)
    crop_right = kwargs.get('crop_right', 100)
    # Total length to average over to find the horizontal lines
    total_width_cols = kwargs.get('total_width_cols', 2000)
    # extra pixels to cut from top and bottom of sample (so we don't get interference from the horizontal lines)
    vertical_crop_extra = kwargs.get('vertical_crop_extra', 50)
    # maximum width [pix] of peaks (ignores peak where dist between minima either side is less than this)
    peak_width_max = kwargs.get('peak_width_max', 80)
    # max distance of peaks from crop lines [pix] (ignores peaks more than [pix] away from the initial crop lines)
    peak_dist_max = kwargs.get('peak_dist_max', 1000)

    # Check the file exists
    if not os.path.isfile(filename):
        print("ERROR:  The filename you entered: " + filename + " does not exist.")
        sys.exit()

    # Get date today
    x = datetime.datetime.now()
    # Set pre-factor for output filename
    output_filename_prefac = (filename[:-4] + "_" +
                              x.strftime("%Y") + x.strftime("%m") +
                              x.strftime("%d") + x.strftime("%H") +
                              x.strftime("%M") + x.strftime("%S") +
                              "_")

    if verbose:
        # Welcome message
        print("  +---------------------------------------------------------------------------------------------------+")
        print("  | This Script reads in an image and attempts to detect vertical and horizontal fiducial marks.      |")
        print("  | The script picks the two marks either side of the centre of the image.                            |")
        print("  | It then calculates the distance between the detected marks and annotates this on an output image. |")
        print("  |  Caution: The calculated distance assumes the input width is supplied correctly                   |")
        print("  |  Kenny Jolley, May 2020                                                                           |")
        print("  +---------------------------------------------------------------------------------------------------+")
        print("   ")

        print(">  Input filename: " + str(filename))
        print(">  Real image width read from commandline: " + str(real_width) + " microns\n")
        # print(">  Output filename prefactor: " + str(output_filename_prefac))

    # Try to load the image in grayscale
    imgdata_original = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    # get dims
    img_width = imgdata_original.shape[1]
    img_height = imgdata_original.shape[0]

    if verbose:
        print(">  Input image width : " + str(img_width) + " Pixels")
        print(">  Input image height: " + str(img_height) + " Pixels")

    # pixel to real width
    length_factor = img_width / real_width  # pixels/ um

    if verbose:
        print(">  There are:   " + str(length_factor) + " Pixels / micron")

    # -- Create an original colour copy to draw on --
    imgdata_original_copy = cv2.cvtColor(imgdata_original, cv2.COLOR_GRAY2BGR)

    # -- Do the initial user defined crop  --

    # Create a copy to modify
    imgdata_cropped = np.copy(imgdata_original)

    # Crop image
    imgdata_cropped = imgdata_cropped[crop_top:(img_height - crop_bottom), crop_left:(img_width - crop_right)]
    # Save the cropped image
    # cv2.imwrite(output_filename_prefac + "cropped.tif", imgdata_cropped)

    # draw crop lines on original copy
    cv2.line(imgdata_original_copy,
             (0, (img_height - crop_bottom)),
             (img_width, (img_height - crop_bottom)), (0, 0, 255), 5)
    cv2.line(imgdata_original_copy,
             (0, crop_top),
             (img_width, crop_top), (0, 0, 255), 5)
    cv2.line(imgdata_original_copy,
             (crop_left, 0),
             (crop_left, img_height), (0, 0, 255), 5)
    cv2.line(imgdata_original_copy,
             ((img_width - crop_right), 0),
             ((img_width - crop_right), img_height), (0, 0, 255), 5)

    # Draw a circle in the centre of the cropped region
    img_centre_x = imgdata_cropped.shape[1] / 2.0
    img_centre_y = imgdata_cropped.shape[0] / 2.0
    cv2.circle(imgdata_original_copy,
               (int(img_centre_x + crop_left), int(img_centre_y + crop_top)),
               10, (0, 255, 0), 3)

    # Draw line and text showing the input width set above (maybe OCR this in the future)
    # Draw double ended arrow
    cv2.arrowedLine(imgdata_original_copy,
                    (0, int(img_height - 0.5 * crop_bottom)),
                    (img_width, int(img_height - 0.5 * crop_bottom)),
                    (255, 0, 255),
                    6,
                    tipLength=0.04)
    cv2.arrowedLine(imgdata_original_copy,
                    (img_width, int(img_height - 0.5 * crop_bottom)),
                    (0, int(img_height - 0.5 * crop_bottom)),
                    (255, 0, 255),
                    6,
                    tipLength=0.04)
    # Write label
    cv2.putText(imgdata_original_copy,
                (str(real_width) + " microns"),
                (int(img_centre_x - 100), int(img_height - 0.5 * crop_bottom - 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                3,
                (255, 0, 255),
                10)

    # -- find horizontal lines on sample (upper and lower edges) ---

    # average central total_width_cols columns
    half_total_width_cols = int(total_width_cols / 2.0)
    avdata = np.average(
        imgdata_cropped[:, int(img_centre_x - half_total_width_cols):int(img_centre_x + half_total_width_cols)],
        axis=1)

    # x coordinate (number 0 to height)
    x = np.linspace(0, avdata.shape[0] - 1, num=avdata.shape[0])

    # plot the average of the image columns vs x
    fig = plt.figure(figsize=(12, 8), dpi=100)
    # Create a new subplot from a grid of 1x1
    ax = fig.add_subplot(111)
    ax.plot(x, avdata, color="blue", linewidth=1.5, linestyle="-", label="raw average")

    # smooth signal with savitzky-golay filter  (multiple small window filters to ensure min location correct)
    for i in range(10):
        avdata = savgol_filter(avdata, 9, 2)  # window size 31, polynomial order 2

    # find maxima and minima
    a = np.diff(np.sign(np.diff(avdata))).nonzero()[0] + 1  # local min+max
    b = (np.diff(np.sign(np.diff(avdata))) > 0).nonzero()[0] + 1  # local min
    c = (np.diff(np.sign(np.diff(avdata))) < 0).nonzero()[0] + 1  # local max

    # plot the filtered signal and detected max, minima
    ax.plot(x, avdata, color="red", linewidth=1.5, linestyle="-", label="savitzky-golay filter")

    ax.plot(x[b], avdata[b], "o", color="green", label="min")
    ax.plot(x[c], avdata[c], "o", color="orange", label="max")
    plt.xlim(0, imgdata_cropped.shape[0])
    # x tick labels
    x = np.zeros(0)
    pix = 0
    while True:
        x = np.append(x, [pix])
        pix += 200
        if pix > imgdata_cropped.shape[0]:
            if pix + 150 > imgdata_cropped.shape[0]:
                x = np.append(x, [imgdata_cropped.shape[0]])
            break
    plt.xticks(x)
    plt.title("Average gray level of each row vs pixel distance from the top")
    plt.xlabel("Distance from top of image, [pixels]")
    plt.ylabel("Average gray level")
    plt.minorticks_on()

    # pick out the two biggest spikes
    # filter broad peaks (width defined above)
    # filter peaks beyond given cutoff (defined above) from crop lines.
    # print(a)
    # print(avdata[a])
    spike1 = 0
    spike2 = 0
    spike1_pix = 0
    spike2_pix = 0
    spike1_h = 0
    spike2_h = 0

    for i in range(len(a) - 2):
        h = (avdata[a[i + 1]] - avdata[a[i]]) + (avdata[a[i + 1]] - avdata[a[i + 2]])
        # find current min spike and overwrite with new value if it is bigger
        # if both the same, just use the first.
        if spike1 == spike2:
            if h > spike1:
                if (a[i + 2] - a[i]) < peak_width_max:
                    if (a[i + 1] < peak_dist_max) or (a[i + 1] > (imgdata_cropped.shape[0] - peak_dist_max)):
                        # print(a[i+1], peak_dist_max, (imgdata_cropped.shape[0]- peak_dist_max ) )
                        spike1 = h
                        spike1_h = avdata[a[i + 1]]
                        spike1_pix = a[i + 1]
        elif spike1 == min(spike1, spike2):
            if h > spike1:
                if (a[i + 2] - a[i]) < peak_width_max:
                    if (a[i + 1] < peak_dist_max) or (a[i + 1] > (imgdata_cropped.shape[0] - peak_dist_max)):
                        # print(a[i+1], peak_dist_max, (imgdata_cropped.shape[0]- peak_dist_max ) )
                        spike1 = h
                        spike1_h = avdata[a[i + 1]]
                        spike1_pix = a[i + 1]
        elif h > spike2:
            if (a[i + 2] - a[i]) < peak_width_max:
                if (a[i + 1] < peak_dist_max) or (a[i + 1] > (imgdata_cropped.shape[0] - peak_dist_max)):
                    # print(a[i+1], peak_dist_max, (imgdata_cropped.shape[0]- peak_dist_max ) )
                    spike2 = h
                    spike2_h = avdata[a[i + 1]]
                    spike2_pix = a[i + 1]

    # text labels
    plt.text(spike1_pix, spike1_h + 3, 'Spike 1')
    plt.text(spike2_pix, spike2_h + 3, 'Spike 2')

    plt.legend(loc="upper center")
    # save plot
    plt.savefig(str(output_filename_prefac) + "sample_vert_edge_detect.pdf", dpi=100)

    if verbose:
        print("Horizontal spike1 peak at ", spike1_pix)
        print("Horizontal spike2 peak at ", spike2_pix)
        print("Distance between horizontal marks: " +
              str(abs(spike2_pix - spike1_pix) / length_factor) + " microns")

    # Draw green crop lines (for region considered in finding horizontal edges)
    cv2.line(imgdata_original_copy,
             (crop_left + int(img_centre_x - half_total_width_cols), 0),
             (crop_left + int(img_centre_x - half_total_width_cols), img_height),
             (0, 255, 0), 2)
    cv2.line(imgdata_original_copy,
             (crop_left + int(img_centre_x + half_total_width_cols), 0),
             (crop_left + int(img_centre_x + half_total_width_cols), img_height),
             (0, 255, 0), 2)

    # Draw yellow lines over the detected horizontal lines in the image
    cv2.line(imgdata_original_copy, (0, spike1_pix + crop_top), (img_width, spike1_pix + crop_top),
             (0, 255, 255), 3)
    cv2.line(imgdata_original_copy, (0, spike2_pix + crop_top), (img_width, spike2_pix + crop_top),
             (0, 255, 255), 3)

    # Draw arrow and write computed distance on the annotated image
    # Draw double ended arrow
    cv2.arrowedLine(imgdata_original_copy,
                    (int(img_width * 0.75), int(spike1_pix + crop_top)),
                    (int(img_width * 0.75), int(spike2_pix + crop_top)),
                    (0, 255, 255),
                    6,
                    tipLength=0.04)
    cv2.arrowedLine(imgdata_original_copy,
                    (int(img_width * 0.75), int(spike2_pix + crop_top)),
                    (int(img_width * 0.75), int(spike1_pix + crop_top)),
                    (0, 255, 255),
                    6,
                    tipLength=0.04)
    # Write label
    cv2.putText(imgdata_original_copy,
                (str(round(abs(spike2_pix - spike1_pix) / length_factor, 3)) + " microns"),
                (int(img_width * 0.75 + 10), int(img_centre_y + crop_top)),
                cv2.FONT_HERSHEY_SIMPLEX,
                3,
                (0, 255, 255),
                10)

    # annotate with crop lines
    cv2.line(imgdata_original_copy,
             (0, (int(min(spike1_pix, spike2_pix) + vertical_crop_extra + crop_top))),
             (img_width, (int(min(spike1_pix, spike2_pix) + vertical_crop_extra + crop_top))),
             (0, 255, 0), 2)
    cv2.line(imgdata_original_copy,
             (0, (int(max(spike1_pix, spike2_pix) - vertical_crop_extra + crop_top))),
             (img_width, (int(max(spike1_pix, spike2_pix) - vertical_crop_extra + crop_top))),
             (0, 255, 0), 2)

    # -- crop vertically ---

    # Create a copy to modify
    imgdata_vertcropped = np.copy(imgdata_cropped)

    # Crop image
    imgdata_vertcropped = imgdata_vertcropped[int(min(spike1_pix, spike2_pix) + vertical_crop_extra):int(
        max(spike1_pix, spike2_pix) - vertical_crop_extra), :]

    # Save the cropped image
    # cv2.imwrite(output_filename_prefac + "vertcropped.tif", imgdata_vertcropped)

    # --  average rows in the cropped image  ---
    avdata = np.average(imgdata_vertcropped, axis=0)

    fig = plt.figure(figsize=(12, 8), dpi=100)
    # Create a new subplot from a grid of 1x1
    ax = fig.add_subplot(111)

    ax.plot(avdata, color="blue", linewidth=1.5, linestyle="-", label="raw average")

    # smoothing filter
    for i in range(10):
        avdata = savgol_filter(avdata, 21, 2)  # window size 201, polynomial order 2

    ax.plot(avdata, color="red", linewidth=1.5, linestyle="-", label="savitzky-golay filter")
    # x coordinate (number 0 to width)
    x = np.linspace(0, avdata.shape[0] - 1, num=avdata.shape[0])
    # detect min and max
    a = np.diff(np.sign(np.diff(avdata))).nonzero()[0] + 1  # local min+max
    b = (np.diff(np.sign(np.diff(avdata))) > 0).nonzero()[0] + 1  # local min
    c = (np.diff(np.sign(np.diff(avdata))) < 0).nonzero()[0] + 1  # local max

    # pick out the two biggest spikes
    # print(a)
    # print(avdata[a])
    vspike1 = 0
    vspike2 = 0
    vspike1_pix = 0
    vspike2_pix = 0
    vspike1_h = 0
    vspike2_h = 0

    for i in range(len(a) - 2):
        h = (avdata[a[i+1]] - avdata[a[i]]) + (avdata[a[i + 1]] - avdata[a[i + 2]])
        # find current min spike and overwrite with new value if it is bigger
        # if both the same, just use the first.
        if vspike1 == vspike2:
            if h > vspike1:
                if (a[i + 2] - a[i]) < peak_width_max:
                    if (a[i + 1] < peak_dist_max) or (a[i + 1] > (imgdata_vertcropped.shape[1] - peak_dist_max)):
                        # print(a[i+1], peak_dist_max, (imgdata_vertcropped.shape[1]- peak_dist_max ) )
                        vspike1 = h
                        vspike1_pix = a[i + 1]
                        vspike1_h = avdata[a[i + 1]]
        elif vspike1 == min(vspike1, vspike2):
            if h > vspike1:
                if (a[i + 2] - a[i]) < peak_width_max:
                    if (a[i + 1] < peak_dist_max) or (a[i + 1] > (imgdata_vertcropped.shape[1] - peak_dist_max)):
                        # print(a[i+1], peak_dist_max, (imgdata_vertcropped.shape[1]- peak_dist_max ) )
                        vspike1 = h
                        vspike1_pix = a[i + 1]
                        vspike1_h = avdata[a[i + 1]]
        elif h > vspike2:
            if (a[i + 2] - a[i]) < peak_width_max:
                if (a[i + 1] < peak_dist_max) or (a[i + 1] > (imgdata_vertcropped.shape[1] - peak_dist_max)):
                    # print(a[i+1], peak_dist_max, (imgdata_vertcropped.shape[1]- peak_dist_max ) )
                    vspike2 = h
                    vspike2_pix = a[i + 1]
                    vspike2_h = avdata[a[i + 1]]

    # text labels
    plt.text(vspike1_pix, vspike1_h + 3, 'Spike 1')
    plt.text(vspike2_pix, vspike2_h + 3, 'Spike 2')

    ax.plot(x[b], avdata[b], "o", color="green", label="min")
    ax.plot(x[c], avdata[c], "o", color="orange", label="max")
    plt.xlim(0, imgdata_vertcropped.shape[1])

    # x tick labels
    x = np.zeros(0)
    pix = 0
    while True:
        x = np.append(x, [pix])
        pix += 500
        if pix > imgdata_vertcropped.shape[1]:
            x = np.append(x, [imgdata_vertcropped.shape[1]])
            break
    plt.xticks(x)

    plt.title("Average gray level of each column vs pixel distance from the left")
    plt.xlabel("Distance from the left of image, [pixels]")
    plt.ylabel("Average gray level")
    plt.minorticks_on()

    plt.legend(loc="upper center")
    plt.savefig(str(output_filename_prefac) + "sample_mark_detect.pdf", dpi=100)

    if verbose:
        print("Vertical spike1 peak at ", vspike1_pix)
        print("Vertical spike2 peak at ", vspike2_pix)
        print(
            "Distance between vertical marks: " + str(abs(vspike2_pix - vspike1_pix) / length_factor) + " microns")

    # Draw blue lines over the detected vertical lines in the image
    cv2.line(imgdata_original_copy,
             (int(min(vspike1_pix, vspike2_pix) + crop_left), 0),
             (int(min(vspike1_pix, vspike2_pix) + crop_left), img_height),
             (255, 100, 0),
             3)

    cv2.line(imgdata_original_copy,
             (int(max(vspike1_pix, vspike2_pix) + crop_left), 0),
             (int(max(vspike1_pix, vspike2_pix) + crop_left), img_height),
             (255, 100, 0),
             3)

    # Draw arrow and write computed distance on the annotated image

    # draw double ended arrow
    cv2.arrowedLine(imgdata_original_copy,
                    (int(min(vspike1_pix, vspike2_pix) + crop_left), int(img_height - crop_bottom - 50)),
                    (int(max(vspike1_pix, vspike2_pix) + crop_left), int(img_height - crop_bottom - 50)),
                    (255, 100, 0),
                    6,
                    tipLength=0.04)
    cv2.arrowedLine(imgdata_original_copy,
                    (int(max(vspike1_pix, vspike2_pix) + crop_left), int(img_height - crop_bottom - 50)),
                    (int(min(vspike1_pix, vspike2_pix) + crop_left), int(img_height - crop_bottom - 50)),
                    (255, 100, 0),
                    6,
                    tipLength=0.04)
    # Write label

    cv2.putText(imgdata_original_copy,
                (str(round((abs(vspike2_pix - vspike1_pix) / length_factor), 3)) + " microns"),
                (int(img_centre_x - 100), int(img_height - crop_bottom - 70)),
                cv2.FONT_HERSHEY_SIMPLEX,
                3,
                (255, 100, 0),
                10)

    # save annotated image
    cv2.imwrite(output_filename_prefac + "annotated.tif", imgdata_original_copy)


# If we are running this script interactively, call the function safely
if __name__ == '__main__':

    # Get the filename and crop options from commandline
    if len(sys.argv) > 2:
        # The first parameter must be the filename
        input_file = str(sys.argv[1])

        # Check the file exists
        if not os.path.isfile(input_file):
            print("ERROR:  The filename you entered: " + input_file + " does not exist.")
            sys.exit()

        # Get width
        input_width = float(sys.argv[2])

        # if there are other parameters, assume they are the crop options in the order: top, bottom, left, right
        # commandline options override the defaults above
        if len(sys.argv) == 3:
            tem_image_analysis_depo_line_detect(verbose=True,
                                                filename=input_file,
                                                img_width=input_width)
        elif len(sys.argv) == 4:
            default_crop_top = int(sys.argv[3])
            tem_image_analysis_depo_line_detect(verbose=True,
                                                filename=input_file,
                                                img_width=input_width,
                                                crop_top=default_crop_top)
        elif len(sys.argv) == 5:
            default_crop_top = int(sys.argv[3])
            default_crop_bottom = int(sys.argv[4])
            tem_image_analysis_depo_line_detect(verbose=True,
                                                filename=input_file,
                                                img_width=input_width,
                                                crop_top=default_crop_top,
                                                crop_bottom=default_crop_bottom)
        elif len(sys.argv) == 6:
            default_crop_top = int(sys.argv[3])
            default_crop_bottom = int(sys.argv[4])
            default_crop_left = int(sys.argv[5])
            tem_image_analysis_depo_line_detect(verbose=True,
                                                filename=input_file,
                                                img_width=input_width,
                                                crop_top=default_crop_top,
                                                crop_bottom=default_crop_bottom,
                                                crop_left=default_crop_left)
        elif len(sys.argv) > 6:
            default_crop_top = int(sys.argv[3])
            default_crop_bottom = int(sys.argv[4])
            default_crop_left = int(sys.argv[5])
            default_crop_right = int(sys.argv[6])
            tem_image_analysis_depo_line_detect(verbose=True,
                                                filename=input_file,
                                                img_width=input_width,
                                                crop_top=default_crop_top,
                                                crop_bottom=default_crop_bottom,
                                                crop_left=default_crop_left,
                                                crop_right=default_crop_right)
    else:
        # Print error and usage, then exit.
        print("\nERROR:  You must define the filename and the image width on the commandline\n")
        print("Usage:")
        print("   TEM_Image_Analysis_Milled_Line_Detect.py  filename  img_width  crop_top  " +
              "crop_bottom  crop_left  crop_right\n")
        print("Filename :   Name of the image file to analyse")
        print("img_width:   Image width in real space units")
        print("crop_top :   Initial crop in pixels (integer) to ignore from the top")
        print("crop_bottom: Initial crop in pixels (integer) to ignore from the bottom")
        print("crop_left:   Initial crop in pixels (integer) to ignore from the left")
        print("crop_right:  Initial crop in pixels (integer) to ignore from the right\n")
        print("The filename and img_width are required, the cropping parameters are optional.")

        sys.exit()
