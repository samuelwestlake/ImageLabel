# ImageLabel
A light weight GUI for labelling objects in images with bounding boxes.
## Labelling Page
The program will load into this page. Images in a given directory will be loaded and presented in alphabetical order. Simply select the class of object you wish to label using the number keys, then click and drag a box around the object.

Once labelled, details of the will be appended to the output. For a given image containing an object of class, 0 wth bounding box coordinages (1,2,8,9) the following would be written:

path/to/image/file.jpg,0,1,2,8,9 

Keypad commands:

- Backspace: Delete the last box drawn
- Space: Skip image
- Return: Save details and go to next image
- Enter: Toggle pages (label and view)

## Viewer Page
