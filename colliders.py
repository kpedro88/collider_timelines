import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import AutoMinorLocator, ScalarFormatter
import matplotlib.patheffects as path_effects
from matplotlib.patches import Rectangle

mpl.use('Agg')
plt.rcParams.update({'font.size': 20})

particles = ["e", "p", "m"]
colors = {
    "e": "#f89c20",
    "p": "#964a8b",
    "m": "#e42536",
#    "i": "#5790fc",
}
legnames = {
    "e": r"$\mathrm{e}^{+}\mathrm{e}^{-}$",
    "p": r"$\mathrm{p}\mathrm{p}$ (or $\mathrm{p}\overline{\mathrm{p}}$)",
    "m": r"$\mu^{+}\mu^{-}$",
}

GeV = 1.0
TeV = 1000.0

colliders = [
    {"name": "PETRA", "start": 1978, "end": 1986, "energy": 20*2*GeV, "particles": ["e"]},
#    {"name": "SLC", "start": 1988, "end": 1998, "energy": 45*2*GeV, "particles": ["e"]},
    {"name": "LEP", "start": 1989, "end": 1995, "energy": 45.6*2*GeV, "particles": ["e"]},
    {"name": "LEP2", "start": 1995, "end": 2000, "energy": 104.5*2*GeV, "particles": ["e"]},
    {"name": "SppS", "start": 1981, "end": 1984, "energy": 315*2*GeV, "particles": ["p"]},
    {"name": "Tevatron (I)", "start": 1992, "end": 1995, "energy": 900*2*GeV, "particles": ["p"]},
    {"name": "Tevatron (II)", "start": 2001, "end": 2011, "energy": 980*2*GeV, "particles": ["p"]},
    {"name": "LHC (1)", "start": 2010, "end": 2013, "energy": 4*2*TeV, "particles": ["p"]},
    {"name": "LHC (2)", "start": 2015, "end": 2018, "energy": 6.5*2*TeV, "particles": ["p"]},
    {"name": "LHC (3)", "start": 2022, "end": 2026, "energy": 6.8*2*TeV, "particles": ["p"]},
    {"name": "HL-LHC", "start": 2029, "end": 2038, "energy": 7*2*TeV, "particles": ["p"]},
]

future_colliders_1 = [
    {"name": "FCC-ee (1)", "start": 2048, "end": 2057, "energy": 240*GeV, "particles": ["e"]},
    {"name": "FCC-ee (2)", "start": 2059, "end": 2063, "energy": 350*GeV, "particles": ["e"]},
    {"name": "FCC-hh", "start": 2074, "end": 2099, "energy": 100*TeV, "particles": ["p"]},
]
future_colliders_2 = [
    {"name": r"$C^{3}$ (1)", "start": 2040, "end": 2051, "energy": 250*GeV, "particles": ["e"]},
    {"name": r"$C^{3}$ (2)", "start": 2053, "end": 2062, "energy": 500*GeV, "particles": ["e"]},
    {"name": r"$C^{3}$ (3)", "start": 2065, "end": 2074, "energy": 2*TeV, "particles": ["e"]},
    {"name": "MuColl (1)", "start": 2045, "end": 2050, "energy": 1*TeV, "particles": ["m"]},
    {"name": "MuColl (2)", "start": 2057, "end": 2062, "energy": 10*TeV, "particles": ["m"]},
]

# corresponds to 9 inches for 60 years (baseline)
figwidth_year = 0.15

def make_collider_plot(colliders, oname):
    # convert to barh arguments
    width = [coll["end"]-coll["start"] for coll in colliders]
    # to have consistent height in log scale
    log_height = 0.2
    y = [coll["energy"] for coll in colliders]
    height = [yy*(10**(log_height/2.)-10**(-log_height/2.)) for yy in y]
    bottom = [yy*10**(-log_height/2.) for yy in y]
    left = [coll["start"] for coll in colliders]
    # todo: handle multiple particles, e.g. e-p colliders
    cols = [colors[coll["particles"][0]] for coll in colliders]
    labels = [coll["name"] for coll in colliders]
    parts = list(set([coll["particles"][0] for coll in colliders]))

    # width computation
    min_year = min([coll["start"] for coll in colliders])
    max_year = max([coll["end"] for coll in colliders])
    figwidth = figwidth_year*(max_year-min_year)

    fig, ax = plt.subplots(figsize=(figwidth, 7))
    bars = ax.barh(bottom, width, height=height, left=left, color=cols, align="edge")
    ax.bar_label(bars, labels=labels, label_type="edge", size=14)
    ax.axvline(x=2023,linestyle='--')
    ax.set_xlabel("year")
    ax.set_ylabel(r"$\sqrt{s}$ [GeV]")
    ax.set_yscale('log')

    handles = [Rectangle((0, 0), 1, 1, fc=colors[particle], fill=True, edgecolor='none', linewidth=0, label=legnames[particle]) for particle in particles if particle in parts]
    ax.legend(handles=handles, loc="lower right")

    plt.savefig("{}.pdf".format(oname), bbox_inches='tight')

make_collider_plot(colliders, "colliders")
make_collider_plot(colliders+future_colliders_1, "colliders_future1")
make_collider_plot(colliders+future_colliders_2, "colliders_future2")
