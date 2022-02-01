# WeChat-Jump-PC
Python3 WeChat Jump on PC
When run this code the window of the Jump Program must be open.
Program uses OpenCV matchTemplate to detct player and Game Over image.
Note that this match Template method is very sensitive to the size and rotation of the template image.
When using this code, please firstly check the size of the very first screenshot, check if the size matches what has been stored in this project.
Then snipshot the player image by your self and replace the temp_player2 image.
This code simulates the mouse press and release actions.
There's a pre-set coordinates in the function jump(), if the coordinates don't fit your situation please change it to a new one.
