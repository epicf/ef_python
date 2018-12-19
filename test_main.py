from os.path import basename
from shutil import copyfile

import pytest

from ef.config.components import TimeGridConf
from ef.config.efconf import EfConf
from main import main


def check_warnings(out, before, after, warning_counts=(0, 1, 2),
                   warning_text="warning: scipy.sparse.linalg.cg info:  1000\n"):
    assert out[:len(before)] == before
    assert out[len(out) - len(after):] == after
    warnings = out[len(before):len(out) - len(after)]
    assert warnings in ("".join([warning_text] * c) for c in warning_counts)


def test_main(mocker, capsys, tmpdir):
    config = tmpdir.join("test_main.conf")
    EfConf(time_grid=TimeGridConf(10, 5, 1)).export_to_fname(str(config))
    mocker.patch("sys.argv", ["main.py", str(config)])
    main()
    expected_before = f"""Config file is:  {config}
[ TimeGrid ]
total_time = 10
time_save_step = 5
time_step_size = 1
[ SpatialMesh ]
grid_x_size = 10.0
grid_x_step = 1.0
grid_y_size = 10.0
grid_y_step = 1.0
grid_z_size = 10.0
grid_z_step = 1.0
[ OutputFilename ]
output_filename_prefix = out_
output_filename_suffix = .h5
[ BoundaryConditions ]
boundary_phi_right = 0.0
boundary_phi_left = 0.0
boundary_phi_bottom = 0.0
boundary_phi_top = 0.0
boundary_phi_near = 0.0
boundary_phi_far = 0.0
[ ParticleInteractionModel ]
particle_interaction_model = PIC
"""
    expected_after = """Writing step 0 to file out_0000000.h5
Time step from 0 to 1 of 10
Time step from 1 to 2 of 10
Time step from 2 to 3 of 10
Time step from 3 to 4 of 10
Time step from 4 to 5 of 10
Writing step 5 to file out_0000005.h5
Time step from 5 to 6 of 10
Time step from 6 to 7 of 10
Time step from 7 to 8 of 10
Time step from 8 to 9 of 10
Time step from 9 to 10 of 10
Writing step 10 to file out_0000010.h5
"""
    out, err = capsys.readouterr()
    assert err == ""
    check_warnings(out, expected_before, expected_after)


def run_example(fname, mocker, capsys, tmpdir):
    tmp = tmpdir.join(basename(fname))
    copyfile(fname, tmp)
    mocker.patch("sys.argv", ["main.py", str(tmp)])
    main()
    out, err = capsys.readouterr()
    assert err == ""


def test_fast_examples(mocker, capsys, tmpdir):
    run_example("examples/minimal_working_example/minimal_conf.conf", mocker, capsys, tmpdir)


@pytest.mark.slowish
def test_medium_examples(mocker, capsys, tmpdir):
    run_example("examples/single_particle_in_free_space/single_particle_in_free_space.conf", mocker, capsys, tmpdir)
    run_example("examples/single_particle_in_magnetic_field/single_particle_in_magnetic_field.conf",
                mocker, capsys, tmpdir)
    run_example("examples/single_particle_in_magnetic_field/large_time_step.conf", mocker, capsys, tmpdir)
    pass


@pytest.mark.slow
def test_slow_examples(mocker, capsys, tmpdir):
    run_example("examples/tube_source_test/contour.conf", mocker, capsys, tmpdir)
    run_example("examples/single_particle_in_radial_electric_field/single_particle_in_radial_electric_field.conf",
                 mocker, capsys, tmpdir)
    run_example("examples/ribbon_beam_contour/contour_bin.conf", mocker, capsys, tmpdir)
    run_example("examples/ribbon_beam_contour/contour.conf", mocker, capsys, tmpdir)
    run_example("examples/drift_tube_potential/pot.conf", mocker, capsys, tmpdir)
    pass
