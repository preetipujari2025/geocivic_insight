#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Windows: add OSGeo4W bin to PATH so that when ctypes loads gdal312.dll
# by full path, Windows can resolve its dependencies (proj, geos, sqlite…).
# PATH-based resolution is required when loading a DLL by absolute path;
# os.add_dll_directory alone is not sufficient in that case.
_gdal_dll_dir = None
if os.name == 'nt':
    _osgeo4w_bin = r'C:\OSGeo4W\bin'
    if os.path.isdir(_osgeo4w_bin) and _osgeo4w_bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = _osgeo4w_bin + os.pathsep + os.environ.get('PATH', '')
        _gdal_dll_dir = os.add_dll_directory(_osgeo4w_bin)  # belt-and-suspenders


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
