from ef.config.efconf import EfConf
from main import main


def test_main(mocker, tmpdir):
    config = tmpdir.join("test_main.conf")
    EfConf().export_to_fname(str(config))
    mocker.patch("sys.argv", ["main.py", str(config)])
    main()
