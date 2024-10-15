# Examples: atlite

Just some `atlite` showcases ...

## AT NUTS3 Capacities

### Setup

Using the environment of PyPSA-Eur, then adding `atlite`, to make sure all dependencies are at some working version.

1. `conda env create -f environment.yaml -n atlite-working -y`
2. `conda activate atlite-working`
3. `pip install nuts-finder --no-dependencies`

### Required Data

- CORINE land use data
- Natura 2000 data

### Further Information

See [atlite docs](https://atlite.readthedocs.io/en/master/examples/landuse-availability.html) for more information, and working with weather cutouts too.

Also compare with [`determine_availability_matrix.py`](https://github.com/PyPSA/pypsa-eur/blob/be83b59302f2d2e90b657d1b39377ddf3b63e1c6/scripts/determine_availability_matrix.py).
