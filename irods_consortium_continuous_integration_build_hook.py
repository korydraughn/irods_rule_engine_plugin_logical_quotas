from __future__ import print_function

import glob
import multiprocessing
import optparse
import os
import tempfile

import irods_python_ci_utilities

def install_building_dependencies(externals_directory):
    externals_list = [
        'irods-externals-boost1.81.0-2',
        'irods-externals-clang16.0.6-0'
    ]

    if externals_directory == 'None' or externals_directory is None:
        irods_python_ci_utilities.install_irods_core_dev_repository()
        irods_python_ci_utilities.install_os_packages(externals_list)
    else:
        package_suffix = irods_python_ci_utilities.get_package_suffix()
        os_specific_directory = irods_python_ci_utilities.append_os_specific_directory(externals_directory)
        externals = []
        for irods_externals in externals_list:
            externals.append(glob.glob(os.path.join(os_specific_directory, irods_externals + '*.{0}'.format(package_suffix)))[0])
        irods_python_ci_utilities.install_os_packages_from_files(externals)
    install_os_specific_dependencies()

def install_os_specific_dependencies_apt():
    irods_python_ci_utilities.install_os_packages(['cmake', 'make', 'gcc'])

def install_os_specific_dependencies_yum():
    irods_python_ci_utilities.install_os_packages(['cmake', 'make', 'gcc', 'curl-devel', 'openssl-devel'])

def install_os_specific_dependencies():
    dispatch_map = {
        'Ubuntu': install_os_specific_dependencies_apt,
        'Debian gnu_linux': install_os_specific_dependencies_apt,
        'Centos': install_os_specific_dependencies_yum,
        'Centos linux': install_os_specific_dependencies_yum,
        'Almalinux': install_os_specific_dependencies_yum,
        'Rocky linux': install_os_specific_dependencies_yum,
        'Opensuse ': install_os_specific_dependencies_yum,
    }
    try:
        return dispatch_map[irods_python_ci_utilities.get_distribution()]()
    except KeyError:
        irods_python_ci_utilities.raise_not_implemented_for_distribution()

def copy_output_packages(build_directory, output_root_directory):
    irods_python_ci_utilities.gather_files_satisfying_predicate(
        build_directory,
        irods_python_ci_utilities.append_os_specific_directory(output_root_directory),
        lambda s:s.endswith(irods_python_ci_utilities.get_package_suffix()))

def main(build_directory, output_root_directory, irods_packages_root_directory, externals_directory):
    install_building_dependencies(externals_directory)
    if irods_packages_root_directory:
        irods_python_ci_utilities.install_irods_dev_and_runtime_packages(irods_packages_root_directory)
    build_directory = os.path.abspath(build_directory or tempfile.mkdtemp(prefix='irods_logical_quotas_plugin_build_directory'))
    irods_python_ci_utilities.subprocess_get_output(['cmake', os.path.dirname(os.path.realpath(__file__))], check_rc=True, cwd=build_directory)
    irods_python_ci_utilities.subprocess_get_output(['make', '-j', str(multiprocessing.cpu_count()), 'package'], check_rc=True, cwd=build_directory)
    if output_root_directory:
        copy_output_packages(build_directory, output_root_directory)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--build_directory')
    parser.add_option('--output_root_directory')
    parser.add_option('--irods_packages_root_directory')
    parser.add_option('--externals_packages_directory')
    options, _ = parser.parse_args()

    main(options.build_directory,
         options.output_root_directory,
         options.irods_packages_root_directory,
         options.externals_packages_directory)
