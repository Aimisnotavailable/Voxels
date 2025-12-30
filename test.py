import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random

# Cube vertices (centered at origin, size 2)
vertices = (
    (-1,  1,  1),  # 0 top-left-front
    ( 1,  1,  1),  # 1 top-right-front
    ( 1, -1,  1),  # 2 bottom-right-front
    (-1, -1,  1),  # 3 bottom-left-front
    (-1,  1, -1),  # 4 top-left-back
    ( 1,  1, -1),  # 5 top-right-back
    ( 1, -1, -1),  # 6 bottom-right-back
    (-1, -1, -1),  # 7 bottom-left-back
)

# Faces defined with CCW winding when viewed from outside
faces = (
    (0, 1, 2, 3),  # front
    (5, 4, 7, 6),  # back
    (4, 0, 3, 7),  # left
    (1, 5, 6, 2),  # right
    (4, 5, 1, 0),  # top
    (3, 2, 6, 7),  # bottom
)

# Per-face normals (pointing outward)
normals = (
    (0.0,  0.0,  1.0),  # front
    (0.0,  0.0, -1.0),  # back
    (-1.0, 0.0,  0.0),  # left
    (1.0,  0.0,  0.0),  # right
    (0.0,  1.0,  0.0),  # top
    (0.0, -1.0,  0.0),  # bottom
)

# Initial colors for each face (RGB floats)
face_colors = [
    [0.8, 0.2, 0.2],  # front - red
    [0.2, 0.8, 0.2],  # back  - green
    [0.2, 0.2, 0.8],  # left  - blue
    [0.8, 0.8, 0.2],  # right - yellow
    [0.8, 0.2, 0.8],  # top   - magenta
    [0.2, 0.8, 0.8],  # bottom- cyan
]

def draw_lit_cube():
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i])
        glColor3fv(face_colors[i])
        for idx in face:
            glVertex3fv(vertices[idx])
    glEnd()

def draw_pick_cube():
    """
    Draw each face with a unique flat color encoding the face index.
    Encoding uses red channel: code = index + 1 (so 0 = no face).
    """
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        code = i + 1
        r = code / 255.0
        glColor3f(r, 0.0, 0.0)
        for idx in face:
            glVertex3fv(vertices[idx])
    glEnd()

def init_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    ambient = (0.12, 0.12, 0.12, 1.0)
    diffuse = (0.85, 0.85, 0.85, 1.0)
    specular = (1.0, 1.0, 1.0, 1.0)

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)

    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 64.0)

def pick_face_at(mouse_x, mouse_y, width, height, rot_x, rot_y, distance):
    """
    Render a pick pass using the same camera and model transforms.
    Returns face index (0..5) or None.
    """
    # Save attributes and matrices we will change
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()

    # Set projection same as main
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, width / float(height), 0.1, 100.0)

    # Set modelview / camera same as main
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, distance,  0.0, 0.0, 0.0,  0.0, 1.0, 0.0)

    # Apply the same object rotations used in the visible render
    glRotatef(rot_y, 0.0, 1.0, 0.0)
    glRotatef(rot_x, 1.0, 0.0, 0.0)

    # Ensure depth test is enabled so occluded faces are not picked
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

    # Disable lighting, texturing, blending, dithering for exact colors
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glDisable(GL_DITHER)

    # Clear and draw pick colors
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_pick_cube()
    glFlush()
    glFinish()

    # Read pixel under mouse (convert y)
    read_x = int(mouse_x)
    read_y = int(height - mouse_y - 1)  # invert y for GL
    pixel = glReadPixels(read_x, read_y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
    # pixel is a bytes-like object; first byte is red channel
    r = pixel[0] if isinstance(pixel, (bytes, bytearray)) else pixel[0]
    face_code = int(r)

    # Restore GL state
    glEnable(GL_DITHER)
    glPopMatrix()  # modelview
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopAttrib()

    if face_code == 0:
        return None
    return face_code - 1

def random_color():
    return [random.uniform(0.1, 0.95) for _ in range(3)]

def main():
    pygame.init()
    W, H = 900, 600
    screen = pygame.display.set_mode((W, H), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Pickable Lit Cube - Click face to change color")

    # Projection (initial)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, W / H, 0.1, 100.0)

    # Interaction state
    distance = 7.0
    rot_x = 20.0
    rot_y = -30.0
    dragging = False
    last_mouse = (0, 0)
    sensitivity = 0.3
    zoom_sensitivity = 0.8

    # Setup GL state and lighting
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, distance,  0.0, 0.0, 0.0,  0.0, 1.0, 0.0)
    init_lighting()
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 5.0, 2.0, 1.0))

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearColor(0.08, 0.08, 0.10, 1.0)

    clock = pygame.time.Clock()
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False

            elif ev.type == MOUSEBUTTONDOWN:
                if ev.button == 1:  # left click: pick face and start drag
                    mx, my = ev.pos
                    # Call pick with current transforms
                    picked = pick_face_at(mx, my, W, H, rot_x, rot_y, distance)
                    if picked is not None:
                        face_colors[picked] = random_color()
                    dragging = True
                    last_mouse = ev.pos
                elif ev.button == 4:  # wheel up
                    distance = max(2.0, distance - zoom_sensitivity)
                elif ev.button == 5:  # wheel down
                    distance = min(50.0, distance + zoom_sensitivity)

            elif ev.type == MOUSEBUTTONUP:
                if ev.button == 1:
                    dragging = False

            elif ev.type == MOUSEMOTION:
                if dragging:
                    x, y = ev.pos
                    lx, ly = last_mouse
                    dx = x - lx
                    dy = y - ly
                    rot_y += dx * sensitivity
                    rot_x += dy * sensitivity
                    rot_x = max(-89.9, min(89.9, rot_x))
                    last_mouse = (x, y)

            elif ev.type == MOUSEWHEEL:
                distance = max(2.0, min(50.0, distance - ev.y * zoom_sensitivity))

            elif ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    running = False

        # Render scene normally
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, distance,  0.0, 0.0, 0.0,  0.0, 1.0, 0.0)
        glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 5.0, 2.0, 1.0))

        glPushMatrix()
        glRotatef(rot_y, 0.0, 1.0, 0.0)
        glRotatef(rot_x, 1.0, 0.0, 0.0)
        draw_lit_cube()
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
