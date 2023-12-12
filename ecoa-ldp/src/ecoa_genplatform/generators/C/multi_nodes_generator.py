# -*- coding: utf-8 -*-
# Copyright (c) 2023 Dassault Aviation
# SPDX-License-Identifier: MIT

import os
from ..force_generation import file_need_generation
from ecoa.utilities.logs import error, info


def generate_multi_nodes_file(output_directory, protection_domains, nodes_deployment, force_flag):
    l_filename = os.path.join(output_directory, 'multi-nodes.py')

    if not nodes_deployment:
        error("fail to generate file 'multi-nodes.py' mandatory with multi nodes")
        return

    if not file_need_generation(l_filename,
                                force_flag,
                                "    multi-nodes.py already exists"):
        return

    info("generate file: %s" % l_filename)

    fd = open(l_filename, 'w')
    text = "#!/usr/bin/env python3\n\
# -*- coding: utf-8 -*-\n\
# Copyright (c) 2023 Dassault Aviation\n\
# SPDX-License-Identifier: MIT\n\
\n\
import warnings\n\
warnings.filterwarnings(action='ignore',message='Python 3.6 is no longer supported')\n\
from multiprocessing import Process\n\
import os, glob\n\
from paramiko import SSHClient\n\
import argparse\n\
import subprocess\n\
\n\
def start_process(dest_dir, user, host, process):\n\
    try:\n\
        client = SSHClient()\n\
        client.load_system_host_keys()\n\
        client.connect(host, username=user)\n\
        stdin, stdout, stderr = client.exec_command(f'cd {dest_dir} && LD_LIBRARY_PATH=. ./{process}')\n\
        print(f\"Process '{process}' running\")\n\
        print(f\"Process '{process}' exit with status\", stdout.channel.recv_exit_status())\n\
    except KeyboardInterrupt:\n\
        print(f\"Closing '{process}'\")\n\
        client.exec_command(f'killall {process}')\n\
        client.close()\n\
\n\
\n\
class ECOA_Multi_Node:\n\
    def __init__(self, deps_dir):\n\
        self.app_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))\n\
        self.deps_dir = deps_dir\n\
        self.user = os.getlogin()\n\
        self.dest_dir = \"/tmp/bin\"\n\
        self.mkdir_cmd = \"ssh {1}@{2} mkdir -p {0}\"\n\
        self.cmd = \"scp -qpr {3} {1}@{2}:{0}\"\n\
        # Create hosts\n"

    text += "        self.hosts = [\"" + '", "'.join(sorted(set(nodes_deployment.values()))) + "\"]\n"

    l_pattern = "%sProcess(target=start_process, args=(self.dest_dir, self.user, \"%s\", \"%s\"))"
    l_processes = [l_pattern % ("", nodes_deployment["main"], "platform")]
    for c_pd in protection_domains.values():
        l_processes.append(l_pattern % ("                          ",
                                        nodes_deployment[c_pd.node],
                                        "PD_" + c_pd.get_name()))

    text += "        # Create platform processes\n\
        self.processes = [" + ',\n'.join(l_processes) + "]"

    text += "\n\
\n\
    def deploy_app(self, host):\n\
        print(\"Deploy ECOA application on '%s'\" % host)\n\
        l_args = ' '.join(glob.glob(\"%s/bin/*\" % self.app_dir))\n\
        l_args += \" %s/lib/libecoa.so\" % self.app_dir\n\
        l_cmd = self.cmd.format(self.dest_dir, self.user, host, l_args)\n\
        subprocess.run(l_cmd.split(\" \"))\n\
\n\
    def deploy_deps(self, host):\n\
        print(\"Deploy ECOA dependencies on '%s'\" % host)\n\
        l_args  = \"%s/lib/liblog4cplus-2.0.so.3 \" % self.deps_dir\n\
        l_args += \"%s/lib/libzlog.so \" % self.deps_dir\n\
        l_args += \"%s/lib/libapr-1.so.0\" % self.deps_dir\n\
        l_cmd = self.cmd.format(self.dest_dir, self.user, host, l_args)\n\
        subprocess.run(l_cmd.split(\" \"))\n\
\n\
    def deploy_platform(self):\n\
        for host in self.hosts:\n\
            if self.deps_dir:\n\
                l_cmd = self.mkdir_cmd.format(self.dest_dir, self.user, host)\n\
                subprocess.run(l_cmd.split(\" \"))\n\
                self.deploy_app(host)\n\
                self.deploy_deps(host)\n\
\n\
    def run_platform(self):\n\
        # Start all platform processes\n\
        for process in self.processes:\n\
            process.start()\n\
        for process in self.processes:\n\
            process.join()\n\
\n\
\n\
    def run(self):\n\
        # Deploy ECOA application and dependencies\n\
        self.deploy_platform()\n\
        # Run ECOA application\n\
        self.run_platform()\n\
\n\
\n\
def parse_args():\n\
    # Parse multi-nodes arguments\n\
\n\
    cmd_parser = argparse.ArgumentParser(description=\"Runs ECOA platform on multiple nodes.\")\n\
    cmd_parser.add_argument('-d', '--deps-dir', action='store', default=\"\",\n\
                            help=\"Deploy ECOA application and dependencies from directory\")\n\
    # return command parser\n\
    return cmd_parser.parse_args()\n\
\n\
\n\
def main():\n\
    # Parse command line\n\
    arguments = parse_args()\n\
    # Launch multi nodes application\n\
    try:\n\
        l_multi_node = ECOA_Multi_Node(arguments.deps_dir)\n\
        l_multi_node.run()\n\
    except KeyboardInterrupt:\n\
        pass\n\
\n\
if __name__ == \"__main__\":\n\
    main()\n"

    print(text, file=fd)

    fd.close()
