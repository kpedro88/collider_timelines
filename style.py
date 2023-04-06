units = {
    "GeV": 1.0,
    "TeV": 1000.0,
}

base_unit = "GeV"

# per year; value corresponds to 9 inches for 60 years (baseline)
fig_width = 0.15

log_height = 0.1
lin_height = 500

particles = {
    "e": {"color": "#f89c20", "name": r"$\mathrm{e}^{+}\mathrm{e}^{-}$"},
    "p": {"color": "#964a8b", "name": r"$\mathrm{p}\mathrm{p}$ (or $\mathrm{p}\overline{\mathrm{p}}$)", "mass": 0.938, "unit": "GeV"},
    "m": {"color": "#e42536", "name": r"$\mu^{+}\mu^{-}$"},
}

font_size = 20
label_size = 14
edge = 'black'
loc = 'upper center'

print_args = {
    "png": {"dpi": 100},
    "pdf": {"bbox_inches": "tight"},
}
