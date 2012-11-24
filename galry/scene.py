import numpy as np
import base64
import json

__all__ = ['SceneCreator', 
           'encode_data', 'decode_data', 'serialize', 'deserialize', ]


# Scene Creator
class SceneCreator(object):
    def __init__(self, constrain_ratio=False,):
        """Initialize the scene."""
        
        # options
        self.constrain_ratio = constrain_ratio
        
        # create an empty scene
        self.scene = {'visuals': [], 'renderer_options': {}}
        
        
    # Visual methods
    # --------------
    def get_visuals(self):
        """Return all visuals defined in the scene."""
        return self.scene['visuals']
        
    def get_visual(self, name):
        visuals = [v for v in self.get_visuals() if v.get('name', '') == name]
        if not visuals:
            return None
        return visuals[0]
        
    
    # Visual creation methods
    # -----------------------
    def add_visual(self, visual_class, *args, **kwargs):
        """Add a visual. This method should be called in `self.initialize`.
        
        A visual is an instanciation of a `DataVisual`. A DataVisual
        defines a pattern for one, or a homogeneous set of plotting objects.
        Example: a text string, a set of rectangles, a set of triangles,
        a set of curves, a set of points. A set of points and rectangles
        does not define a visual since it is not an homogeneous set of
        objects. The technical reason for this distinction is that OpenGL
        allows for very fast rendering of homogeneous objects by calling
        a single rendering command (even if several objects of the same type
        need to be rendered, e.g. several rectangles). The lower the number
        of rendering calls, the better the performance.
        
        Hence, a visual is defined by a particular DataVisual, and by
        specification of fields in this visual (positions of the points,
        colors, text string for the example of the TextVisual, etc.). It
        also comes with a number `N` which is the number of vertices contained
        in the visual (N=4 for one rectangle, N=len(text) for a text since 
        every character is rendered independently, etc.)
        
        Several visuals can be created in the PaintManager, but performance
        decreases with the number of visuals, so that all homogeneous 
        objects to be rendered on the screen at the same time should be
        grouped into a single visual (e.g. multiple line plots).
        
        Arguments:
          * visual_class=None: the visual class, deriving from
            `Visual` (or directly from the base class `DataVisual`
            if you don't want the navigation-related functionality).
          * visible=True: whether this visual should be rendered. Useful
            for showing/hiding a transient element. When hidden, the visual
            does not go through the rendering pipeline at all.
          
        Returns:
          * visual: a dictionary containing all the information about
            the visual, and that can be used in `set_data`.
        
        """
        # get the name of the visual from kwargs
        name = kwargs.pop('name', 'visual%d' % (len(self.get_visuals())))
        if self.get_visual(name):
            raise ValueError("Visual name '%s' already exists." % name)
        # pass constrain_ratio to all visuals
        if 'constrain_ratio' not in kwargs:
            kwargs['constrain_ratio'] = self.constrain_ratio
        # create the visual object
        visual = visual_class(self.scene, *args, **kwargs)
        # get the dictionary version
        dic = visual.get_dic()
        dic['name'] = name
        # append the dic to the visuals list of the scene
        self.get_visuals().append(dic)
        return visual
        
        
    # Output methods
    # --------------
    def get_scene(self):
        return self.scene

    def serialize(self):
        return serialize(self.scene)
        
    def from_json(self, scene_json):
        self.scene = deserialize(scene_json)
        

# Scene serialization methods
# ---------------------------
def encode_data(data):
    """Return the Base64 encoding of a Numpy array."""
    return base64.b64encode(data)
        
def decode_data(s, dtype=np.float32):
    """Return a Numpy array from its encoded Base64 string. The dtype
    must be provided (float32 by default)."""
    return np.fromstring(base64.b64decode(s), dtype=dtype)

class ArrayEncoder(json.JSONEncoder):
    """JSON encoder that handles Numpy arrays and serialize them with base64
    encoding."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return encode_data(obj)
        return json.JSONEncoder.default(self, obj)
        
def serialize(scene):
    """Serialize a scene."""
    return json.dumps(scene, cls=ArrayEncoder)

def deserialize(scene_json):
    """Deserialize a scene."""
    scene = json.loads(scene_json)
    for visual in scene.get('visuals', []):
        for variable in visual.get('variables', []):
            tp = type(variable.get('data', None))
            if tp == str or tp == unicode:
                vartype = variable.get('vartype', 'float')
                if vartype == 'int':
                    dtype = np.int32
                elif vartype == 'float':
                    dtype = np.float32
                variable['data'] = decode_data(variable['data'], dtype)
            
    return scene


if __name__ == '__main__':
    
    data = np.array([0., 10.], dtype=np.int32)
    
    scene = {'visuals':
    [
        {'name': 'position',
        'variables':
            [
            {
                'data': data,
                'vartype': 'int',
            }
            ],
        'vertex_shader':"""void main(){}""",
        }
    ],
    'renderer_options':{}
    }
    
    scene_json = serialize(scene)
    
    scene2 = deserialize(scene_json)
    
    from pprint import pprint
    pprint(scene)
    print
    pprint(scene2)
    
        
        