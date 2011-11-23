from nose.tools import assert_equals, assert_not_equals
from trashcli.trash2 import EmptyCmd

from StringIO import StringIO
import os

class TestEmptyCmd():
    def setUp(self):
        require_empty_dir('.local')
        self.out=StringIO()
        self.err=StringIO()
        self.environ = { 'XDG_DATA_HOME': '.local' }
    def run(self):
        EmptyCmd(
            out = self.out, 
            err = self.err, 
            environ = self.environ).run('trash-empty')

    def test_it_removes_an_info_file(self):
        touch(                    '.local/Trash/info/foo.trashinfo')
        self.run()
        assert not os.path.exists('.local/Trash/info/foo.trashinfo')

    def test_it_removes_multiple_info_files(self):
        touch('.local/Trash/info/foo.trashinfo')
        touch('.local/Trash/info/bar.trashinfo')
        touch('.local/Trash/info/baz.trashinfo')
        assert_not_equals([],list(os.listdir('.local/Trash/info/')))

        self.run()

        assert_equals([],list(os.listdir('.local/Trash/info/')))

    def test_it_removes_files(self):
        touch('.local/Trash/info/foo.trashinfo')
        touch('.local/Trash/files/foo')
        assert_not_equals([],list(os.listdir('.local/Trash/files/')))

        self.run()

        assert_equals([],list(os.listdir('.local/Trash/files/')))
    
    def test_it_keep_unknown_files_in_infodir(self):
        touch('.local/Trash/info/not-a-trashinfo')

        self.run()

        assert os.path.exists('.local/Trash/info/not-a-trashinfo')

    def test_it_removes_orphan_files(self):
        touch(                    '.local/Trash/files/a-file-without-any-associated-trashinfo')
        assert os.path.exists(    '.local/Trash/files/a-file-without-any-associated-trashinfo')

        self.run()

        assert not os.path.exists('.local/Trash/files/a-file-without-any-associated-trashinfo')

class TestEmptyCmdWithTime:

    def test_it_keeps_files_newer_than_N_days(self):

        self.make_trashinfo('foo', '2000-01-01')
        self.set_now('2000-01-01')

        self.run_trash_emtpy('2')

        assert os.path.exists(self.trashinfo('foo'))

    def test_it_removes_files_older_than_N_days(self):

        self.make_trashinfo('foo', '1999-01-01')
        self.set_now('2000-01-01')

        self.run_trash_emtpy('2')

        assert not os.path.exists(self.trashinfo('foo'))

    def setUp(self):
        self.xdg_data_home='.local'
        require_empty_dir(self.xdg_data_home)

    def make_trashinfo(self, name, date):
        contents = "DeletionDate=%sT00:00:00\n" % date
        write_file(self.trashinfo(name), contents) 

    def trashinfo(self, name):
        return '%(dirname)s/Trash/info/%(name)s.trashinfo' % {
                    'dirname' : self.xdg_data_home,
                    'name'    : name }

    def set_now(self, yyyy_mm_dd):
        self.now = lambda: date(yyyy_mm_dd)

    def run_trash_emtpy(self, *args):
        empty=EmptyCmd(
                out=StringIO(), 
                err=StringIO(), 
                environ={'XDG_DATA_HOME':self.xdg_data_home},
                now=self.now
                )
        empty.run('trash-empty', *args)

from nose import SkipTest
class TestEmptyCmdWithMultipleVolumes:
    def test_it_removes_trashinfos_from_method_1_dir(self):
        raise SkipTest()
        require_empty_dir('.fake_root')
        touch('.fake_root/media/external-disk/.Trash/123/info/foo')
        empty=EmptyCmd(
                out=StringIO(), 
                err=StringIO(), 
                environ={},
                getuid=lambda: 123,
                list_volumes=lambda: ['.fake_root/media/external-disk'],
                )
        empty.run('trash-empty')
        assert not os.path.exists('.fake_root/media/external-disk/.Trash/123/info/foo')

def touch(filename):
    write_file(filename, '')
    assert os.path.isfile(filename)

def write_file(filename, contents):
    import os
    parent = os.path.dirname(filename)
    if not os.path.isdir(parent): os.makedirs(parent)
    file(filename, 'w').write(contents)
    assert_equals(file(filename).read(), contents)


def require_empty_dir(dirname):
    import os
    import shutil
    if os.path.exists(dirname): shutil.rmtree(dirname)
    os.makedirs(dirname)
    assert os.path.isdir(dirname)

def date(yyyy_mm_dd):
    from datetime import datetime
    return datetime.strptime(yyyy_mm_dd, '%Y-%m-%d')

