import math
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter
import matplotlib.patheffects as path_effects
from matplotlib.patches import Rectangle
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from matplotlib.offsetbox import AnchoredText
from matplotlib import _api

# utility functions

'''
Text placement options (using 'loc' convention):
              |              |              
  upper left  | upper center | upper right  
______________|______________|______________
              |(0,1)    (1,1)|              
              |              |              
  center left |    center    | center right (right)
              |    (BOX)     |              
              |(0,0)    (1,0)|              
¯¯¯¯¯¯¯¯¯¯¯¯¯¯|¯¯¯¯¯¯¯¯¯¯¯¯¯¯|¯¯¯¯¯¯¯¯¯¯¯¯¯¯
  lower left  | lower center | lower right  
              |              |              

BboxBase.corners() returns [[x0, y0], [x0, y1], [x1, y0], [x1, y1]]
augment w/: [[x0, yc], [xc, y0], [x1, yc], [xc, y1], [xc, yc]]

translation to alignment & data coords:
desired      | va, ha @ point
upper left   | bottom, right  @ (0,1) -> [1]
upper center | bottom, center @ (½,1) -> [7]
upper right  | bottom, left   @ (1,1) -> [3]
center left  | center, right  @ (0,½) -> [4]
center       | center, center @ (½,½) -> [8]
center right | center, left   @ (1,½) -> [6]
lower left   | top, right     @ (0,0) -> [0]
lower center | top, center    @ (½,0) -> [5]
lower right  | top, left      @ (1,0) -> [2]

s, kwargs will be passed to annotate() call
'''
def annotateAroundBox(s, loc, ax, bbox, **kwargs):
    # only want to deal with str version
    reverse_codes = {val:key for key,val in AnchoredText.codes.items()}
    list_codes = list(AnchoredText.codes.keys())
    # loc conversions
    loc_to_actual = {
        'upper left': {'va': 'bottom', 'ha': 'right', 'index': 1},
        'upper center': {'va': 'bottom', 'ha': 'center', 'index': 7},
        'upper right': {'va': 'bottom', 'ha': 'left', 'index': 3},
        'center left': {'va': 'center', 'ha': 'right', 'index': 4},
        'center': {'va': 'center', 'ha': 'center', 'index': 8},
        'center right': {'va': 'center', 'ha': 'left', 'index': 6},
        'lower left': {'va': 'top', 'ha': 'right', 'index': 0},
        'lower center': {'va': 'top', 'ha': 'center', 'index': 5},
        'lower right': {'va': 'top', 'ha': 'left', 'index': 2},
    }
    loc_to_actual['right'] = loc_to_actual['center right']
    # validate and convert loc
    if not isinstance(loc, str):
        loc = _api.check_getitem(reverse_codes, loc=loc)
    else:
        _api.check_in_list(list_codes, loc=loc)

    # get corners and add center points
    points = bbox.corners().tolist()
    x0 = points[0][0]
    x1 = points[3][0]
    y0 = points[0][1]
    y1 = points[3][1]
    xc = (x0+x1)/2.
    yc = (y0+y1)/2.
    points.extend([[x0,yc],[xc,y0],[x1,yc],[xc,y1],[xc,yc]])

    # create annotation in desired location
    actual = loc_to_actual[loc]
    actual['xy'] = points[actual.pop('index')]
    actual['xycoords'] = 'data'
    kwargs.update(actual)
    an = ax.annotate(s, **kwargs)
    return an

# set up path for configs
def config_path(basedir="", configdir="colliders"):
    import os,sys
    if len(basedir)==0: basedir = os.getcwd()
    sys.path.append("{}/{}".format(basedir,configdir))

def import_attrs(pyname, attrs=()):
    if not attrs==() and not isinstance(attrs,list):
        attrs = [attrs]
    tmp = __import__(pyname.replace(".py","").replace("/","."), fromlist=attrs)
    if attrs==():
        return tmp
    elif len(attrs)==1:
        return getattr(tmp,attrs[0])
    else:
        return [getattr(tmp,attr) for attr in attrs]

def make_collider_plot(collider_file, style_file, oname, formats, livingston, liny):
    config_path()
    colliders = import_attrs(collider_file,"colliders")
    style = import_attrs(style_file)

    plt.rcParams.update({'font.size': style.font_size})

    # convert to barh arguments
    energy = [coll["energy"]*style.units[coll["unit"]] for coll in colliders]
    yname = r"$\sqrt{s}$"
    # convert from cm energy to Livingston style
    if livingston:
        def convert_livingston(value):
            factor = 2*style.particles["p"]["mass"]*style.units[style.particles["p"]["unit"]]
            return value**2/factor
        energy = [convert_livingston(en) for en in energy]
        yname = "Particle energy"
        style.lin_height = convert_livingston(2*style.lin_height)

    # to have consistent height in log scale
    if not liny:
        height = [en*(10**(style.log_height/2.)-10**(-style.log_height/2.)) for en in energy]
        yvals = [en*10**(-style.log_height/2.) for en in energy] # corresponds to bottom of bar
    else:
        height = style.lin_height
        yvals = energy

    # x axis arguments
    width = [coll["end"]-coll["start"] for coll in colliders]
    left = [coll["start"] for coll in colliders]

    # todo: handle multiple particles, e.g. e-p colliders
    colors = [style.particles[coll["particles"][0]]["color"] for coll in colliders]
    labels = [coll["name"] for coll in colliders]
    locs = [coll["loc"] if "loc" in coll else style.loc for coll in colliders]
    parts = list(set([coll["particles"][0] for coll in colliders]))

    # width computation
    min_year = min([coll["start"] for coll in colliders])
    max_year = max([coll["end"] for coll in colliders])
    fig_width = style.fig_width*(max_year-min_year)
    fig, ax = plt.subplots(figsize=(fig_width, 7))
    bars = ax.barh(yvals, width, height=height, left=left, color=colors, label=labels, edgecolor=style.edge, linewidth=1)
    patches = {p.get_label() : p.get_bbox() for p in bars.patches}
    bar_labels = [annotateAroundBox(label, loc, ax, patches[label], size=style.label_size) for label, loc in zip(labels,locs)]
    ax.axvline(x=2023.25,linestyle='--')
    ax.set_xlabel("year")
    ax.set_ylabel("{} [{}]".format(yname,style.base_unit))
    if not liny: ax.set_yscale('log')

    handles = [Rectangle((0, 0), 1, 1, fc=style.particles[particle]["color"], fill=True, edgecolor='none', linewidth=0, label=style.particles[particle]["name"]) for particle in style.particles if particle in parts]
    ax.legend(handles=handles, loc="lower right")

    plt.tight_layout()
    for pformat in formats:
        plt.savefig("{}.{}".format(oname,pformat), **style.print_args[pformat])

if __name__=="__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-C", "--colliders", type=str, default="current", help="name of colliders config file")
    parser.add_argument("-S", "--style", type=str, default="style", help="name of style file")
    parser.add_argument("-o", "--output", type=str, default="colliders", help="name for output image file(s)")
    parser.add_argument("-f", "--format", type=str, default=["pdf","png"], nargs='+', help="format(s) for output image files")
    parser.add_argument("-l", "--livingston", default=False, action="store_true", help="Livingston plot style: show s/(2m_proton) instead of sqrt(s)")
    parser.add_argument("--liny", default=False, action="store_true", help="use linear y scale")
    args = parser.parse_args()

    make_collider_plot(args.colliders, args.style, args.output, args.format, args.livingston, args.liny)
