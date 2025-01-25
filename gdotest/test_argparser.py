from gdotest.TestUtil import GDOTestCase


class test_argparser(GDOTestCase):
    def setUp(self):
        Application.init(os.path.dirname(__file__) + "/../")
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)

