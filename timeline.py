import math
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter
import matplotlib.patheffects as path_effects
from matplotlib.patches import Rectangle
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# utility functions

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
        align = "edge"
    else:
        height = style.lin_height
        yvals = energy
        align = "center"

    # x axis arguments
    width = [coll["end"]-coll["start"] for coll in colliders]
    left = [coll["start"] for coll in colliders]

    # todo: handle multiple particles, e.g. e-p colliders
    colors = [style.particles[coll["particles"][0]]["color"] for coll in colliders]
    labels = [coll["name"] for coll in colliders]
    parts = list(set([coll["particles"][0] for coll in colliders]))

    # width computation
    min_year = min([coll["start"] for coll in colliders])
    max_year = max([coll["end"] for coll in colliders])
    fig_width = style.fig_width*(max_year-min_year)

    fig, ax = plt.subplots(figsize=(fig_width, 7))
    bars = ax.barh(yvals, width, height=height, left=left, color=colors, align=align)
    ax.bar_label(bars, labels=labels, label_type="edge", size=14)
    ax.axvline(x=2023,linestyle='--')
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
