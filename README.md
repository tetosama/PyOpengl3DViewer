
# pyopengl 3d viewer

This is a study purpose python application.

You could display obj files, play animations, highlight vertices or triangles to display their positions and indices, track a vertex to see its position history during the animation, etc.


## Usage
This application could display obj file, and animations.

To load an obj file, simply have

`model = OBJLoader('your_obj_name')` 
in the code.

To move around, use right-button of the mouse to rotate, and wasd to move.

To load an animation, use

` loadAnimation <your_animation_file.json>` or simply ` la <your_animation_file.json>` in terminal.

After the animation is loaded, you could play the animation by typing

` animation animate <start_index> <end_index> <time_for_each_frame> ` in terminal.

You could also stop animation by

` animation stop `

Goto a certain frame by

` animation goto <frame_index>`

Track a vertex by 

` animation track <vertex_index> `

The example format of animation is provided in the json files.

You could highlight a vertex or triangle by typing command in terminal:

` animation highlight v <vertex_index> `

` animation highlight t <triangle_index> `

You could also highlight vertices and triangles by clicking, the buttons are on the UI.


