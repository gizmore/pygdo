from gdo.base.Application import Application
from gdo.base.Database import Database
from gdo.base.Logger import Logger
from gdo.base.Util import Strings
from gdo.core import module_core
from gdo.core.GDO_Cronjob import GDO_Cronjob
from gdo.core.MethodCronjob import MethodCronjob
from gdo.base.ModuleLoader import ModuleLoader
from gdo.date.Time import Time
from gdo.core.module_core import module_core

class Cronjob:
    FORCE: bool = False

    @classmethod
    def run(cls, force: bool = False) -> None:
        cls.FORCE = force
        loader = ModuleLoader.instance()
        loader.load_modules_db()
        loader.init_modules(True, True)
        GDO_Cronjob.cleanup()
        for name, module in loader._cache.items():
            for method in module.get_methods():
                if isinstance(method, MethodCronjob):
                    if cls.should_run(method):
                        Logger.cron(f"Starting {method.get_sqn()}")
                        entry = GDO_Cronjob.blank({
                            'cron_method': method.get_sqn(),
                        }).insert()
                        db = Application.db()
                        try:
                            db.begin()
                            method.gdo_execute()
                            db.commit()
                            entry.save_val('cron_success', '1')
                        except Exception as ex:
                            Logger.exception(ex)
                            db.rollback()
                            entry.save_val('cron_success', '0')
                        finally:
                            Logger.cron(f"Finished {method.get_sqn()}")


    @classmethod
    def should_run(cls, method: MethodCronjob) -> bool:
        if GDO_Cronjob.table().get_by_vals({'cron_method': method.get_sqn(), 'cron_success': '2'}):
            return False

        if Cronjob.FORCE:
            return True

        mod = module_core.instance()
        dt = mod.cfg_last_cron().timestamp()
        dt = int(dt)
        dt = dt - dt % 60
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
            at.upper(), {
                'MON': '1',
                'TUE': '2',
                'WED': '3',
                'THU': '4',
                'FRI': '5',
                'SAT': '6',
                'SUN': '7',
            }
        )
        att = Time.get_date(timestamp,'i H j m N').split()
        matches = 0
        for i, a in enumerate(at.split()):
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
