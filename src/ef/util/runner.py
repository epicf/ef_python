import os
import shlex
import subprocess
import tempfile

from ef.config.efconf import EfConf


class EfRunner:
    def __init__(self, conf=EfConf(), ef_command="python3 ../../main.py"):
        self.conf = conf
        self.command = ef_command

    def _configure_and_run(self, workdir, config_fname, config_file):
        self.conf.export_to_file(config_file)
        config_file.close()
        self.run_from_file(config_fname, workdir)

    def run(self, workdir="./", save_config_as=None):
        if save_config_as is None:
            config_fd, config_fname = tempfile.mkstemp(suffix=".ini", text=True)
            config_file = os.fdopen(config_fd, 'w')
        else:
            config_fname = save_config_as
            config_file = open(config_fname, 'w')
        self._configure_and_run(workdir, config_fname, config_file)
        if save_config_as is None:
            os.remove(config_fname)

    def run_from_file(self, startfile, workdir="./"):
        current_dir = os.getcwd()
        os.chdir(workdir)
        command = self.command + " " + startfile
        print("command:", command)
        # https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        for stdout_line in iter(process.stdout.readline, None):
            if stdout_line:
                print(stdout_line.strip())
            else:
                break
        process.stdout.close()
        ret_code = process.wait()
        if ret_code:
            print("warning: return code is", ret_code)
        os.chdir(current_dir)
        return ret_code


def main():
    runner = EfRunner(EfConf(), 'python3 ../main.py')
    runner.run()


if __name__ == "__main__":
    main()
