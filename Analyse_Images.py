#!/usr/bin/env python
#
# Example code for calling the analysis functions.

from TEM_Image_Analysis_Milled_Line_Detect import tem_image_analysis_milled_line_detect


filename = "Example_Data/Milled_Images/Gilsocarbon/40Cup.tif"

tem_image_analysis_milled_line_detect(verbose=True,
                                      filename=filename,
                                      img_width=17.0,
                                      crop_top=400,
                                      crop_bottom=500,
                                      crop_left=500,
                                      crop_right=100,
                                      total_width_cols=1500)

filename = "Example_Data/Milled_Images/Gilsocarbon/600C up_003.tif"

tem_image_analysis_milled_line_detect(verbose=True,
                                      filename=filename,
                                      img_width=17.0,
                                      crop_top=400,
                                      crop_bottom=500,
                                      crop_left=500,
                                      crop_right=100,
                                      total_width_cols=1500)


filename = "Example_Data/Milled_Images/Copper/100CR.tif"

tem_image_analysis_milled_line_detect(verbose=True,
                                      filename=filename,         # filename
                                      img_width=25.0,            # Real image width in microns
                                      crop_top=1000,             # pixels to crop from the top
                                      crop_bottom=1100,          # pixels to crop from the bottom
                                      crop_left=100,             # pixels to crop from the left
                                      crop_right=100,            # pixels to crop from the right
                                      total_width_cols=4000)     # image width about centre to use for horizontal line

filename = "Example_Data/Milled_Images/Copper/350C R.tif"

tem_image_analysis_milled_line_detect(verbose=True,
                                      filename=filename,         # filename
                                      img_width=25.0,            # Real image width in microns
                                      crop_top=1200,             # pixels to crop from the top
                                      crop_bottom=1100,          # pixels to crop from the bottom
                                      crop_left=100,             # pixels to crop from the left
                                      crop_right=100,            # pixels to crop from the right
                                      total_width_cols=4000)     # image width about centre to use for horizontal line
