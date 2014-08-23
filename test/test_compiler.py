"""
Tests the compiler module
"""
import re
import pytest
from open_cobol_ide import system
from open_cobol_ide.compiler import GnuCobolCompiler, FileType, \
    GnuCobolStandard
from open_cobol_ide.settings import Settings


def test_extensions():
    exts = GnuCobolCompiler().extensions
    if system.windows:
        assert exts[0] == '.exe'
        assert exts[1] == '.dll'
    else:
        assert exts[0] == ''
        assert exts[1] == '.so'


def test_is_working():
    assert GnuCobolCompiler().is_working()


def test_get_version():
    prog = re.compile(r'^\d.\d.\d$')
    assert prog.match(GnuCobolCompiler().get_version()) is not None


@pytest.mark.parametrize('file_type, expected', [
    (FileType.EXECUTABLE, '.exe' if system.windows else ''),
    (FileType.MODULE, '.dll' if system.windows else '.so'),
])
def test_type_extension(file_type, expected):
    assert GnuCobolCompiler().extension_for_type(file_type) == expected


exe_ext = GnuCobolCompiler().extension_for_type(FileType.EXECUTABLE)
dll_ext = GnuCobolCompiler().extension_for_type(FileType.MODULE)

@pytest.mark.parametrize('free, std, ftype, expected_opts',[
    (False, GnuCobolStandard.default, FileType.EXECUTABLE, [
        '-x',
        '-o HelloWorld' + exe_ext,
        '-std=default'
    ]),
    (True, GnuCobolStandard.default, FileType.EXECUTABLE, [
        '-x',
        '-o HelloWorld' + exe_ext,
        '-std=default',
        '-free'
    ]),
    (False, GnuCobolStandard.default, FileType.MODULE, [
        '-o HelloWorld' + dll_ext,
        '-std=default'
    ]),
    (True, GnuCobolStandard.default, FileType.MODULE, [
        '-o HelloWorld' + dll_ext,
        '-std=default',
        '-free'
    ]),
    (False, GnuCobolStandard.mf, FileType.EXECUTABLE, [
        '-x',
        '-o HelloWorld' + exe_ext,
        '-std=mf'
    ]),
    (True, GnuCobolStandard.mf, FileType.EXECUTABLE, [
        '-x',
        '-o HelloWorld' + exe_ext,
        '-std=mf',
        '-free'
    ]),
    (False, GnuCobolStandard.mf, FileType.MODULE, [
        '-o HelloWorld' + dll_ext,
        '-std=mf'
    ]),
    (True, GnuCobolStandard.mf, FileType.MODULE, [
        '-o HelloWorld' + dll_ext,
        '-std=mf',
        '-free'
    ])
])
def test_make_command_exe(free, std, ftype, expected_opts):
    compiler = GnuCobolCompiler()
    settings = Settings()
    settings.free_format = free
    settings.cobol_standard = std
    pgm, options = compiler.make_command('HelloWorld.cbl', ftype)
    assert pgm == 'cobc'
    for o, eo in zip(options, expected_opts):
        assert o == eo
    settings.free_format = free
    settings.cobol_standard = GnuCobolStandard.default
    settings.free_format = False


def test_compile():
    assert GnuCobolCompiler().compile(
        'test/testfiles/HelloWorld.cbl', FileType.EXECUTABLE) == 0
