Ef is a software for simulation of charged particles dynamics.
It's primary areas of application are accelerator science and plasma physics.

# About ef

## Examples

<p align="center">
<a href="https://github.com/epicf/ef/wiki/Single-Particle-In-Uniform-Magnetic-Field"><img src="https://github.com/epicf/ef/blob/dev/doc/figs/single_particle_in_magnetic_field/3d.png" width="400"/></a>
<a href="https://github.com/epicf/ef/wiki/Ribbon-Beam-Contour"><img src="https://raw.githubusercontent.com/epicf/ef/dev/doc/figs/ribbon_beam_contour/countour_beam.png" width="250"/>
</a>
<br>
<a href="https://github.com/epicf/ef/wiki/Single-Particle-In-Uniform-Magnetic-Field">Single particle in uniform magnetic field;</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://github.com/epicf/ef/wiki/Ribbon-Beam-Contour">Widening of a ribbon beam during the propagation</a>
</p>

<p align="center">
<br>
<a href="https://github.com/epicf/ef/wiki/Contour-of-Ribbon-Beam-In-Uniform-Magnetic-Field"><img src="https://github.com/epicf/ef/raw/dev/doc/figs/ribbon_beam_in_magnetic_field_contour/mgn_field_ribbon_contour.png" width="300"/></a>
<br>
<a href="https://github.com/epicf/ef/wiki/Contour-of-Ribbon-Beam-In-Uniform-Magnetic-Field">Ribbon beam in uniform magnetic field</a>
</p>

<p align="center">
<br>
<a href="https://github.com/epicf/ef/wiki/Potential-well-of-cylindrical-beam-in-tube"><img src="https://github.com/epicf/ef/blob/dev/doc/figs/potential_well_of_beam_in_tube/potential.png" width="300"/></a>
<a href="https://github.com/epicf/ef/wiki/Child-Langmuir-Law-for-Planar-Diode"><img src="https://github.com/epicf/ef/blob/dev/doc/figs/ex5_diode_childs_law/diode_VC.png" width="300"/></a>
<br>
<a href="https://github.com/epicf/ef/wiki/Potential-well-of-cylindrical-beam-in-tube">Potential of electron beam inside conducting tube;</a>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://github.com/epicf/ef/wiki/Child-Langmuir-Law-for-Planar-Diode">Volt-Ampere characteristic of a planar diode</a>
</p>

## Physics

### Motivation

Ef focuses on non-relativistic energies.
Particular emphasis is placed on low-energy beams, such that can be found in ion sources and electron guns.
A motivation behind the program, the scope and the general goals are discussed [here](https://github.com/epicf/ef/wiki/Motivation-and-Goals).

### Particle-in-cell

Particles dynamics is traced under action of external electromagnetic fields.
Particle self-interaction is taken into account with [particle-in-cell](https://github.com/epicf/ef/wiki/What-It-Is-and-How-It-Works#intuitive-introduction-to-particle-in-cell-method) method. Detailed description of the mathematical model can be found [here](https://github.com/epicf/ef/wiki/What-It-Is-and-How-It-Works#mathematical-model-description).

## CAD plans

Attention is given to integration with CAD software to allow for simulation of complex real-life experimental setups.
An experimental plugin for FreeCAD [exists](https://github.com/epicf/ef/wiki/Freecad-and-Paraview).

## Versions

Ef is a free software -- it's source code is open and avaible for
modification and redistribution.
Python (this one) and [C++](https://github.com/epicf/ef) versions are available.
Python version is easy to install and experiment with.
It's speed should be sufficient to perform example computations and small-scale
simulations but for large-scale simulations C++ version is the choice.

## Status

[Current features](https://github.com/epicf/ef/wiki/Current-Features-and-Development-Roadmap)
are described in detail in appropriate wiki sections,
as well as [installation procedure](https://github.com/epicf/ef/wiki/Installation).
Some usage [examples](https://github.com/epicf/ef/wiki/Examples) are also given.

# For users

## Install

It's advisable to use a virtual python environment:
```sh
virtualenv --python=python3 ef_venv
. ef_venv/bin/activate
```

EF is not available in pypi yet, install from github:
```sh
pip install 'git+https://github.com/epicf/ef_python.git'
```

## Run

Start simulation defined by my_config.conf:
```sh
ef my_config.conf
```

Continue simulation from hdf5 file my_0005.h5:
```sh
ef my_0005.h5
```

# For developers

## Install for development

```sh
git clone https://github.com/epicf/ef_python.git
cd ef_python
virtualenv --python=python3 venv
. venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Test

Install pytest:
```sh
pip install pytest pytest-mock
```

Run fast unittests:
```sh
pytest
```

Run more tests (including slower examples)
```sh
pytest -m 'not (slow)'
```

Run every test (including slow simulation examples)
```sh
pytest -m ''
```

## Run tests with tox

More python versions and test types.

-   Install tox: `pip install tox`
-   Run `tox`

Can also run in parallel with `detox`.

## Run

Start simulation defined by my_config.conf:
```sh
ef my_config.conf
```

Continue simulation from hdf5 file my_0005.h5:
```sh
ef my_0005.h5
```
