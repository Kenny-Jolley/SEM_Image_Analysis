# SEM_Image_Analysis
Python scripts for analysing SEM images.
The scripts read in an image and then detects the vertical and horizontal fiducial marks.
It then calculates the distance between the detected marks and annotates this on an output image.


## Requirements

This code requires [Python](http://www.python.org) to run. Currently Python 3.6+ should work. 
Scripts have the following dependencies:  
- OpenCV  (Version 4.1+ should work)  
- Numpy  
- Scipy  
- Matplotlib  


## Installation

Clone the repository to a directory of your choice:
~~~
 git clone git://github.com/Kenny-Jolley/SEM_Image_Analysis.git
~~~


## Usage

The scripts are best used via the commandline.  You should call the script and pass the filename of the image as an argument.

For example:
`SEM_Image_Analysis_Milled_Line_Detect.py  filename  img_width  crop_top crop_bottom  crop_left  crop_right`  

- Filename :   Name of the image file to analyse
- img_width:   Image width in real space units
- crop_top :   Initial crop in pixels (integer) to ignore from the top
- crop_bottom: Initial crop in pixels (integer) to ignore from the bottom
- crop_left:   Initial crop in pixels (integer) to ignore from the left
- crop_right:  Initial crop in pixels (integer) to ignore from the right

The filename and img_width are required, the cropping parameters are optional.

        

### Example Images

This folder contains a collection of example images that can be analysed by the scripts.  
To analyse all the example images, just run the script: `Analyse_Images.py`  




