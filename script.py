import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1

    vary = False;
    frames = False;
    basename = False;

    for i in range(len(commands)):
        if commands[i]['op'] == "vary":
            vary = True;
        elif commands[i]['op'] == 'frames':
            frames = True;
            num_frames = commands[i]['args'][0];
        elif commands[i]['op'] == 'basename':
            basename = True;
            name = commands[i]['args'][0];

    if vary and not frames:
        quit();

    if (frames and not basename):
        print("Basename: image");
        name = "image";

    if (not frames):
        num_frames = 1;

    return (name, int(num_frames));

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]

    for i in range(len(commands)):
        if commands[i]['op'] == 'vary':
            start_frame = commands[i]['args'][0];
            end_frame = commands[i]['args'][1];
            start_var = commands[i]['args'][2];
            end_var = commands[i]['args'][3];
            knobname = commands[i]['knob'];

            increment = (end_var - start_var)/(end_frame - start_frame);
            current = start_var - increment;

            for j in range(int(start_frame), int(end_frame + 1), 1):
                frames[j][knobname] = current + increment;
                current = current + increment;


    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)


    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 20
    consts = ''
    coords = []
    coords1 = []
    shading = 'flat'

    for i in range(len(frames)):
        for k, v in frames[i].items():
            symbols[k] = v;
        for command in commands:
            #print(command)
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                if (command['knob'] != None):
                    tmp = make_translate(args[0] * symbols[command['knob']], args[1] * symbols[command['knob']], args[2] * symbols[command['knob']])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                if (command['knob'] != None):
                    tmp = make_scale(args[0] * symbols[command['knob']], args[1] * symbols[command['knob']], args[2] * symbols[command['knob']])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180);
                if (command['knob'] != None):
                    theta = args[1] * (math.pi/180) * symbols[command['knob']]
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            elif c == 'shading':
                shading = command['shade_type'];
            elif c == 'mesh':
                if command['constants']:
                    reflect = command['constants']
                read_obj(tmp, args[0]);
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect, shading);
            # end operation loop
        if (len(frames) > 1):
            save_extension(screen, "anim/" + name + f"%03d"%i);
            print("Saved Frame: " + "anim/" + name + f"%03d"%i);

            tmp = new_matrix()
            ident( tmp )

            stack = [ [x[:] for x in tmp] ]
            screen = new_screen()
            zbuffer = new_zbuffer()
            tmp = []

    if len(frames) > 1:
        make_animation(name);
