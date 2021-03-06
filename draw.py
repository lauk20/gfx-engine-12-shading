from display import *
from matrix import *
from gmath import *
from collections import defaultdict
import time

vertex_map = { };
#firstpoly = "false"
def draw_scanline(x0, z0, x1, z1, y, screen, zbuffer, c0, c1, shading = 'flat', lighting = None):
    #print(c0, c1, "NOW");
    if x0 > x1:
        tx = x0
        tz = z0
        x0 = x1
        z0 = z1
        x1 = tx
        z1 = tz

        if shading != "phongaaa":
            tc = c0;
            c0 = c1;
            c1 = tc;



    x = x0
    z = z0
    delta_z = (z1 - z0) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0

    if (shading == "gouraud"):
        color = c0[:];
        delta_color_r = (c1[0] - c0[0]) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0;
        delta_color_g = (c1[1] - c0[1]) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0;
        delta_color_b = (c1[2] - c0[2]) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0

        while x <= x1:
            ncolor = color[:];
            for i in range(3):
                ncolor[i] = int(ncolor[i]);
            limit_color(ncolor);

            plot(screen, zbuffer, ncolor, x, y, z)
            x+= 1
            z+= delta_z

            color[0]+= delta_color_r;
            color[1]+= delta_color_g;
            color[2]+= delta_color_b;
    elif (shading == "phong"):
        #"color" is actually the interpolated normal
        color = c0[:];
        delta_color_r = (c1[0] - c0[0]) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0;
        delta_color_g = (c1[1] - c0[1]) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0;
        delta_color_b = (c1[2] - c0[2]) / (x1 - x0 + 1) if (x1 - x0 + 1) != 0 else 0

        while x <= x1:
            normal = color[:];

            phong = get_lighting(normal, lighting[0], lighting[1], lighting[2], lighting[3], lighting[4]);
            plot(screen, zbuffer, phong, x, y, z)
            x+= 1
            z+= delta_z

            color[0]+= delta_color_r;
            color[1]+= delta_color_g;
            color[2]+= delta_color_b;
    else:
        while x <= x1:
            plot(screen, zbuffer, c0, x, y, z)
            x+= 1
            z+= delta_z


def scanline_convert(polygons, i, screen, zbuffer, color, shading, colorMap = None, v1 = None, v2 = None, v3 = None, lighting = None):
    flip = False
    BOT = 0
    TOP = 2
    MID = 1

    points = [ (polygons[i][0], polygons[i][1], polygons[i][2]),
               (polygons[i+1][0], polygons[i+1][1], polygons[i+1][2]),
               (polygons[i+2][0], polygons[i+2][1], polygons[i+2][2]) ]

    # alas random color, we hardly knew ye
    #color = [0,0,0]
    #color[RED] = (23*(i/3)) %256
    #color[GREEN] = (109*(i/3)) %256
    #color[BLUE] = (227*(i/3)) %256

    points.sort(key = lambda x: x[1])
    x0 = points[BOT][0]
    z0 = points[BOT][2]
    x1 = points[BOT][0]
    z1 = points[BOT][2]
    y = int(points[BOT][1])

    distance0 = int(points[TOP][1]) - y * 1.0 + 1
    distance1 = int(points[MID][1]) - y * 1.0 + 1
    distance2 = int(points[TOP][1]) - int(points[MID][1]) * 1.0 + 1

    dx0 = (points[TOP][0] - points[BOT][0]) / distance0 if distance0 != 0 else 0
    dz0 = (points[TOP][2] - points[BOT][2]) / distance0 if distance0 != 0 else 0
    dx1 = (points[MID][0] - points[BOT][0]) / distance1 if distance1 != 0 else 0
    dz1 = (points[MID][2] - points[BOT][2]) / distance1 if distance1 != 0 else 0


    tpointsTOP = points[TOP][:];
    tpointsMID = points[MID][:];
    tpointsBOT = points[BOT][:];

    pointsTOP = [0, 0, 0];
    pointsMID = [0, 0, 0];
    pointsBOT = [0, 0, 0];

    for i in range(3):
        pointsTOP[i] = round(tpointsTOP[i], 3);
        pointsMID[i] = round(tpointsMID[i], 3);
        pointsBOT[i] = round(tpointsBOT[i], 3);

    pointsTOP = tuple(pointsTOP);
    pointsMID = tuple(pointsMID);
    pointsBOT = tuple(pointsBOT);

    #GOURAUD SHADING
    if (shading == 'gouraud'):
        #print(tpointsTOP);
        #print(pointsTOP);

        colorTOP = colorMap[pointsTOP];
        colorMID = colorMap[pointsMID];
        colorBOT = colorMap[pointsBOT];

        #print(colorTOP, colorMID, colorBOT);

        #interpolation of color on edges
        di0r = (colorTOP[0] - colorBOT[0]) / distance0 if distance0 != 0 else 0;
        di0g = (colorTOP[1] - colorBOT[1]) / distance0 if distance0 != 0 else 0;
        di0b = (colorTOP[2] - colorBOT[2]) / distance0 if distance0 != 0 else 0;

        di1r = (colorMID[0] - colorBOT[0]) / distance1 if distance1 != 0 else 0;
        di1g = (colorMID[1] - colorBOT[1]) / distance1 if distance1 != 0 else 0;
        di1b = (colorMID[2] - colorBOT[2]) / distance1 if distance1 != 0 else 0;

        c0 = colorBOT[:];
        c1 = colorBOT[:];

        #print(di1r, di1g, di1b, "di1r di1g di1b");
        """
        print(di0r, di1r, "di0r di1r")

        print(colorTOP, colorMID, colorBOT, "top mid bot");
        print(pointsTOP, pointsMID, pointsBOT, "top mid bot");
        """
        while y <= int(points[TOP][1]):
            if ( not flip and y >= int(points[MID][1])):
                #print("FLIPFPFIFIPFIPFPFPIFIPPFIIPFPFPF")
                flip = True

                dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
                dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0

                di1r = (colorTOP[0] - colorMID[0]) / distance2 if distance2 != 0 else 0;
                di1g = (colorTOP[1] - colorMID[1]) / distance2 if distance2 != 0 else 0;
                di1b = (colorTOP[2] - colorMID[2]) / distance2 if distance2 != 0 else 0;

                x1 = points[MID][0]
                z1 = points[MID][2]
                c1 = colorMID[:];

                """
                print(c0, c1, "before flip");
                print(c0, c1, "after flip");
                print(int(x0), int(x1), y, "x0 x1 y");
                """
            #draw_line(int(x0), y, z0, int(x1), y, z1, screen, zbuffer, color)
            """
            print(colorTOP, colorMID, colorBOT, "BEFORE top mid bot");
            print(c0, c1, "BEFORE c0 c1");
            """
            draw_scanline(int(x0), z0, int(x1), z1, y, screen, zbuffer, c0, c1, 'gouraud')
            x0+= dx0
            z0+= dz0
            x1+= dx1
            z1+= dz1

            c0[0]+= di0r;
            c0[1]+= di0g;
            c0[2]+= di0b;

            c1[0]+= di1r;
            c1[1]+= di1g;
            c1[2]+= di1b;

            """
            print(colorTOP, colorMID, colorBOT, "AFTER top mid bot");
            print(c0, c1, "AFTER c0 c1");
            """

            y+= 1
    elif shading == 'phong': #phong code turned out to be exactly the same as gouraud
        colorTOP = colorMap[pointsTOP];
        colorMID = colorMap[pointsMID];
        colorBOT = colorMap[pointsBOT];

        #print(colorTOP, colorMID, colorBOT);

        #interpolation of color on edges
        di0r = (colorTOP[0] - colorBOT[0]) / distance0 if distance0 != 0 else 0;
        di0g = (colorTOP[1] - colorBOT[1]) / distance0 if distance0 != 0 else 0;
        di0b = (colorTOP[2] - colorBOT[2]) / distance0 if distance0 != 0 else 0;

        di1r = (colorMID[0] - colorBOT[0]) / distance1 if distance1 != 0 else 0;
        di1g = (colorMID[1] - colorBOT[1]) / distance1 if distance1 != 0 else 0;
        di1b = (colorMID[2] - colorBOT[2]) / distance1 if distance1 != 0 else 0;

        c0 = colorBOT[:];
        c1 = colorBOT[:];

        #print(di1r, di1g, di1b, "di1r di1g di1b");
        """
        print(di0r, di1r, "di0r di1r")

        print(colorTOP, colorMID, colorBOT, "top mid bot");
        print(pointsTOP, pointsMID, pointsBOT, "top mid bot");
        """
        while y <= int(points[TOP][1]):
            if ( not flip and y >= int(points[MID][1])):
                #print("FLIPFPFIFIPFIPFPFPIFIPPFIIPFPFPF")
                flip = True

                dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
                dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0

                di1r = (colorTOP[0] - colorMID[0]) / distance2 if distance2 != 0 else 0;
                di1g = (colorTOP[1] - colorMID[1]) / distance2 if distance2 != 0 else 0;
                di1b = (colorTOP[2] - colorMID[2]) / distance2 if distance2 != 0 else 0;

                x1 = points[MID][0]
                z1 = points[MID][2]
                c1 = colorMID[:];

                """
                print(c0, c1, "before flip");
                print(c0, c1, "after flip");
                print(int(x0), int(x1), y, "x0 x1 y");
                """
            #draw_line(int(x0), y, z0, int(x1), y, z1, screen, zbuffer, color)
            """
            print(colorTOP, colorMID, colorBOT, "BEFORE top mid bot");
            print(c0, c1, "BEFORE c0 c1");
            """
            draw_scanline(int(x0), z0, int(x1), z1, y, screen, zbuffer, c0, c1, 'phong', lighting)
            x0+= dx0
            z0+= dz0
            x1+= dx1
            z1+= dz1

            c0[0]+= di0r;
            c0[1]+= di0g;
            c0[2]+= di0b;

            c1[0]+= di1r;
            c1[1]+= di1g;
            c1[2]+= di1b;

            """
            print(colorTOP, colorMID, colorBOT, "AFTER top mid bot");
            print(c0, c1, "AFTER c0 c1");
            """

            y+= 1
    else:
        while y <= int(points[TOP][1]):
            if ( not flip and y >= int(points[MID][1])):
                flip = True

                dx1 = (points[TOP][0] - points[MID][0]) / distance2 if distance2 != 0 else 0
                dz1 = (points[TOP][2] - points[MID][2]) / distance2 if distance2 != 0 else 0

                x1 = points[MID][0]
                z1 = points[MID][2]

            draw_scanline(int(x0), z0, int(x1), z1, y, screen, zbuffer, color, color)
            x0+= dx0
            z0+= dz0
            x1+= dx1
            z1+= dz1

            y+= 1

    """
    global firstpoly
    firstpoly = "true"
    """

def add_polygon( polygons, x0, y0, z0, x1, y1, z1, x2, y2, z2 ):
    add_point(polygons, x0, y0, z0)
    add_point(polygons, x1, y1, z1)
    add_point(polygons, x2, y2, z2)

def draw_polygons( polygons, screen, zbuffer, view, ambient, light, symbols, reflect, shading):
    if len(polygons) < 2:
        print('Need at least 3 points to draw')
        return

    for i in range(0, len(polygons), 3):
        hashKey = tuple([round(polygons[i][0], 3), round(polygons[i][1], 3), round(polygons[i][2], 3), round(polygons[i][3], 3)]);

        if hashKey in vertex_map:
            vertex_map[hashKey].append(i);
        else:
            vertex_map[hashKey] = [i];

        hashKey = tuple([round(polygons[i + 1][0], 3), round(polygons[i + 1][1], 3), round(polygons[i + 1][2], 3), round(polygons[i + 1][3], 3)]);

        if hashKey in vertex_map:
            vertex_map[hashKey].append(i);
        else:
            vertex_map[hashKey] = [i];

        hashKey = tuple([round(polygons[i + 2][0], 3), round(polygons[i + 2][1], 3), round(polygons[i + 2][2], 3), round(polygons[i + 2][3], 3)]);

        if hashKey in vertex_map:
            vertex_map[hashKey].append(i);
        else:
            vertex_map[hashKey] = [i];

        #print(vertex_map);
        #time.sleep(5);

    point = 0
    while point < len(polygons) - 2:

        normal = calculate_normal(polygons, point)[:]

        #print normal
        if normal[2] > 0:

            color = get_lighting(normal, view, ambient, light, symbols, reflect )

            vertex_normal1 = get_vertex_normal(polygons[point], vertex_map, polygons);
            vertex_normal2 = get_vertex_normal(polygons[point + 1], vertex_map, polygons);
            vertex_normal3 = get_vertex_normal(polygons[point + 2], vertex_map, polygons);

            edge1 = polygons[point][0:3];
            edge2 = polygons[point + 1][0:3];
            edge3 = polygons[point + 2][0:3];
            for i in range(3):
                edge1[i] = round(edge1[i], 3);
                edge2[i] = round(edge2[i], 3);
                edge3[i] = round(edge3[i], 3);

            if (shading == 'gouraud'):
                color_1 = get_lighting(vertex_normal1, view, ambient, light, symbols, reflect);
                color_2 = get_lighting(vertex_normal2, view, ambient, light, symbols, reflect);
                color_3 = get_lighting(vertex_normal3, view, ambient, light, symbols, reflect);

                edge1 = polygons[point][0:3];
                edge2 = polygons[point + 1][0:3];
                edge3 = polygons[point + 2][0:3];
                for i in range(3):
                    edge1[i] = round(edge1[i], 3);
                    edge2[i] = round(edge2[i], 3);
                    edge3[i] = round(edge3[i], 3);

                colorMap = {
                            tuple(edge1) : color_1,
                            tuple(edge2) : color_2,
                            tuple(edge3) : color_3
                            };

                scanline_convert(polygons, point, screen, zbuffer, color, shading, colorMap);

            elif (shading == 'phong'):
                colorMap = {
                    tuple(edge1) : vertex_normal1,
                    tuple(edge2) : vertex_normal2,
                    tuple(edge3) : vertex_normal3
                }
                scanline_convert(polygons, point, screen, zbuffer, color, shading, colorMap, vertex_normal1, vertex_normal2, vertex_normal3, [view, ambient, light, symbols, reflect]);
            else:
                scanline_convert(polygons, point, screen, zbuffer, color, shading);

            # draw_line( int(polygons[point][0]),
            #            int(polygons[point][1]),
            #            polygons[point][2],
            #            int(polygons[point+1][0]),
            #            int(polygons[point+1][1]),
            #            polygons[point+1][2],
            #            screen, zbuffer, color)
            # draw_line( int(polygons[point+2][0]),
            #            int(polygons[point+2][1]),
            #            polygons[point+2][2],
            #            int(polygons[point+1][0]),
            #            int(polygons[point+1][1]),
            #            polygons[point+1][2],
            #            screen, zbuffer, color)
            # draw_line( int(polygons[point][0]),
            #            int(polygons[point][1]),
            #            polygons[point][2],
            #            int(polygons[point+2][0]),
            #            int(polygons[point+2][1]),
            #            polygons[point+2][2],
            #            screen, zbuffer, color)
        point+= 3

#obj reader
def read_obj(polygons, filename):
    filename = filename;
    file = open(filename);
    line = file.readline();
    vertices = []
    face_count = 0;
    while line:
        args = line.split();
        if (len(args) > 0 and args[0] == 'v'):
            vertices.append([float(args[1]), float(args[2]), float(args[3]), 1.0])
        elif (len(args) > 0 and args[0] == 'f'):
            face_count+= 1;
            polygons.append(vertices[int(args[1]) - 1][:]);
            polygons.append(vertices[int(args[2]) - 1][:]);
            polygons.append(vertices[int(args[3]) - 1][:]);
        line = file.readline();

    #print(face_count);

def add_box( polygons, x, y, z, width, height, depth ):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon(polygons, x, y, z, x1, y1, z, x1, y, z)
    add_polygon(polygons, x, y, z, x, y1, z, x1, y1, z)

    #back
    add_polygon(polygons, x1, y, z1, x, y1, z1, x, y, z1)
    add_polygon(polygons, x1, y, z1, x1, y1, z1, x, y1, z1)

    #right side
    add_polygon(polygons, x1, y, z, x1, y1, z1, x1, y, z1)
    add_polygon(polygons, x1, y, z, x1, y1, z, x1, y1, z1)
    #left side
    add_polygon(polygons, x, y, z1, x, y1, z, x, y, z)
    add_polygon(polygons, x, y, z1, x, y1, z1, x, y1, z)

    #top
    add_polygon(polygons, x, y, z1, x1, y, z, x1, y, z1)
    add_polygon(polygons, x, y, z1, x, y, z, x1, y, z)
    #bottom
    add_polygon(polygons, x, y1, z, x1, y1, z1, x1, y1, z)
    add_polygon(polygons, x, y1, z, x, y1, z1, x1, y1, z1)

def add_sphere(polygons, cx, cy, cz, r, step ):
    points = generate_sphere(cx, cy, cz, r, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    step+= 1
    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * step + longt
            p1 = p0+1
            p2 = (p1+step) % (step * (step-1))
            p3 = (p0+step) % (step * (step-1))

            if longt != step - 2:
                add_polygon( polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p1][0],
                             points[p1][1],
                             points[p1][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2])
            if longt != 0:
                add_polygon( polygons, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2],
                             points[p3][0],
                             points[p3][1],
                             points[p3][2])


def generate_sphere( cx, cy, cz, r, step ):
    points = []

    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation/float(step)
        for circle in range(circ_start, circ_stop+1):
            circ = circle/float(step)

            x = r * math.cos(math.pi * circ) + cx
            y = r * math.sin(math.pi * circ) * math.cos(2*math.pi * rot) + cy
            z = r * math.sin(math.pi * circ) * math.sin(2*math.pi * rot) + cz

            points.append([x, y, z])
            #print 'rotation: %d\tcircle%d'%(rotation, circle)
    return points

def add_torus(polygons, cx, cy, cz, r0, r1, step ):
    points = generate_torus(cx, cy, cz, r0, r1, step)

    lat_start = 0
    lat_stop = step
    longt_start = 0
    longt_stop = step

    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * step + longt;
            if (longt == (step - 1)):
                p1 = p0 - longt;
            else:
                p1 = p0 + 1;
            p2 = (p1 + step) % (step * step);
            p3 = (p0 + step) % (step * step);

            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p3][0],
                        points[p3][1],
                        points[p3][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2] )
            add_polygon(polygons,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2],
                        points[p1][0],
                        points[p1][1],
                        points[p1][2] )


def generate_torus( cx, cy, cz, r0, r1, step ):
    points = []
    rot_start = 0
    rot_stop = step
    circ_start = 0
    circ_stop = step

    for rotation in range(rot_start, rot_stop):
        rot = rotation/float(step)
        for circle in range(circ_start, circ_stop):
            circ = circle/float(step)

            x = math.cos(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cx;
            y = r0 * math.sin(2*math.pi * circ) + cy;
            z = -1*math.sin(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cz;

            points.append([x, y, z])
    return points


def add_circle( points, cx, cy, cz, r, step ):
    x0 = r + cx
    y0 = cy
    i = 1

    while i <= step:
        t = float(i)/step
        x1 = r * math.cos(2*math.pi * t) + cx;
        y1 = r * math.sin(2*math.pi * t) + cy;

        add_edge(points, x0, y0, cz, x1, y1, cz)
        x0 = x1
        y0 = y1
        i+= 1

def add_curve( points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type ):

    xcoefs = generate_curve_coefs(x0, x1, x2, x3, curve_type)[0]
    ycoefs = generate_curve_coefs(y0, y1, y2, y3, curve_type)[0]

    i = 1
    while i <= step:
        t = float(i)/step
        x = t * (t * (xcoefs[0] * t + xcoefs[1]) + xcoefs[2]) + xcoefs[3]
        y = t * (t * (ycoefs[0] * t + ycoefs[1]) + ycoefs[2]) + ycoefs[3]
        #x = xcoefs[0] * t*t*t + xcoefs[1] * t*t + xcoefs[2] * t + xcoefs[3]
        #y = ycoefs[0] * t*t*t + ycoefs[1] * t*t + ycoefs[2] * t + ycoefs[3]

        add_edge(points, x0, y0, 0, x, y, 0)
        x0 = x
        y0 = y
        i+= 1


def draw_lines( matrix, screen, zbuffer, color ):
    if len(matrix) < 2:
        print('Need at least 2 points to draw')
        return

    point = 0
    while point < len(matrix) - 1:
        draw_line( int(matrix[point][0]),
                   int(matrix[point][1]),
                   matrix[point][2],
                   int(matrix[point+1][0]),
                   int(matrix[point+1][1]),
                   matrix[point+1][2],
                   screen, zbuffer, color)
        point+= 2

def add_edge( matrix, x0, y0, z0, x1, y1, z1 ):
    add_point(matrix, x0, y0, z0)
    add_point(matrix, x1, y1, z1)

def add_point( matrix, x, y, z=0 ):
    matrix.append( [x, y, z, 1] )



def draw_line( x0, y0, z0, x1, y1, z1, screen, zbuffer, color ):

    #swap points if going right -> left
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False

    if ( abs(x1-x0) >= abs(y1 - y0) ): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x + 1
        if ( A > 0 ): #octant 1
            d = A + B/2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B/2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y) + 1
        if ( A > 0 ): #octant 2
            d = A/2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A/2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -1 * B
            loop_start = y1
            loop_end = y

    dz = (z1 - z0) / distance if distance != 0 else 0

    while ( loop_start < loop_end ):
        plot( screen, zbuffer, color, x, y, z )
        if ( (wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
             (tall and ((A > 0 and d < 0) or (A < 0 and d > 0 )))):

            x+= dx_northeast
            y+= dy_northeast
            d+= d_northeast
        else:
            x+= dx_east
            y+= dy_east
            d+= d_east
        z+= dz
        loop_start+= 1
    plot( screen, zbuffer, color, x, y, z )
