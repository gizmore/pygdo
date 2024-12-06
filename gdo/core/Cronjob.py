from gdo.base.Application import Application
from gdo.base.Database import Database
from gdo.base.Logger import Logger
from gdo.base.Util import Strings
from gdo.core.GDO_Cronjob import GDO_Cronjob
from gdo.core.MethodCronjob import MethodCronjob
from gdo.base.ModuleLoader import ModuleLoader
from gdo.date.Time import Time


class Cronjob:
    FORCE = False

    @classmethod
    def run(cls, force: bool = False) -> None:
        Cronjob.FORCE = force
        loader = ModuleLoader.instance()
        modules = loader.load_modules_db()
        loader.init_modules(True, True)
        # GDO_Cronjob.cleanup()
        for name, module in loader._cache.items():
            for method in module.get_methods():
                if isinstance(method, MethodCronjob):
                    if cls.should_run(method):
                        Logger.debug("CRON!")
                        method.gdo_execute()
            # Module_Cronjob.instance().setLastRun()

    #
    # @staticmethod
    # def runCronjob(entry: str, path: str, module: GDO_Module) -> None:
    #     method = Installer.loopMethod(module, path)
    #     if isinstance(method, MethodCronjob):
    #         if Cronjob.shouldRun(method):
    #             Cronjob.executeCronjob(method)

    @classmethod
    def should_run(cls, method: MethodCronjob) -> bool:
        if GDO_Cronjob.table().get_by_vals({'cron_method': method.fqn(), 'cron_success': '2'}):
            return False

        if Cronjob.FORCE:
            return True

        # module = Module_Cronjob.instance()
        # lastRun = module.cfgLastRun()
        dt = Time.parse_datetime_db()DateTimeDB(lastRun)
        minute = dt.format('Y-m-d H:i')
        dt = Time.parseDateDB(minute)
        now = Application.TIME
        while dt <= now:
            if Cronjob.should_run_at(method, dt):
                return True
            dt += Time.ONE_MINUTE
        return False

    @classmethod
    def should_run_at(cls, method: MethodCronjob, timestamp: int) -> bool:

        at = method.gdo_run_at()
        at = Strings.replace_all(
            at, {
                'MON': '1',
                'TUE': '2',
                'WED': '3',
                'THU': '4',
                'FRI': '5',
                'SAT': '6',
                'SUN': '7',
            }
        )
        att = Time.format(Time.ONE_MINUTE * timestamp, 'i H j m N').split()
        matches = 0
        for i, a in enumerate(at):
            aa = a.split(',')
            for aaa in aa:
                if aaa == '*':
                    matches += 1
                    break
                if '-' in aaa:
                    aaa = map(int, aaa.split('-'))
                    for j in range(aaa[0], aaa[1] + 1):
                        if att[i] == str(j):
                            matches += 1
                            break
                elif aaa.startswith('/'):
                    aaa = int(aaa[1:])
                    if int(att[i]) % aaa == 0:
                        matches += 1
                        break
                elif att[i] == aaa:
                    matches += 1
                    break
        return matches == 5

    @staticmethod
    def executeCronjob(method: MethodCronjob) -> None:
        try:
            db = Application.db()
            job = GDO_Cronjob.blank({'cron_method': method.__class__.__name__}).insert()
            db.transactionBegin()
            method.execute()
            job.saveVars({'cron_success': '1'})
            db.transactionEnd()
        except Exception as ex:
            if 'db' in locals():
                db.transactionRollback()
                if 'job' in locals():
                    job.saveVars({'cron_success': '0'})
            raise ex