from asyncio import iscoroutine

from gdo.base.Application import Application
from gdo.base.Method import Method
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Query import Query
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Index import GDT_Index
from gdo.core.GDT_Method import GDT_Method
from gdo.core.GDT_Serialize import GDT_Serialize, Mode
from gdo.date.GDT_Created import GDT_Created
from gdo.date.Time import Time
from gdo.base.Util import CLI


class GDO_Event(GDO):

    def gdo_cached(self) -> bool:
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            # No AutoInc!
            GDT_Enum('event_type').choices({'to_web': 'To Web', 'to_cli': 'To CLI', 'to_dog': 'To Dog'}).not_null(),
            GDT_Method('event_name').ascii().case_s().maxlen(64).not_null(),
            GDT_Serialize('event_args').mode(Mode.JSON),
            GDT_Created('event_created'),
            GDT_Index('event_index_type').index_fields('event_type', 'event_created').using_btree(),
        ]

    #########
    # Write #
    #########
    @classmethod
    def to_cli(cls, event_name: str, args: any = None):
        cls.to_sink('to_cli', event_name, args)

    @classmethod
    def to_dog(cls, event_name: str, args: any = None):
        cls.to_sink('to_dog', event_name, args)

    @classmethod
    def to_web(cls, event_name: str, args: any = None):
        cls.to_sink('to_web', event_name, args)

    @classmethod
    def to_sink(cls, sink: str, event_name: str, args: any = None):
        return cls.blank({
            'event_type': sink,
            'event_name': event_name,
            'event_args': cls.table().column('event_args').to_val(args),
        }).insert()

    ########
    # Read #
    ########
    @classmethod
    def query_for_sink(cls, sink: str, ts_min: float) -> Query:
        cut = Time.get_date(ts_min)
        return cls.table().select().where(f"event_type='{sink}' AND event_created >= '{cut}'")

    #######
    # Get #
    #######
    def get_event_method(self) -> Method:
        module, method = self.gdo_val('event_name').split('.')
        return ModuleLoader.instance().get_module_method(module, method)

    def get_event_args(self) -> any:
        return self.gdo_value('event_args')

    ########
    # Exec #
    ########

    def execute_cli(self):
        method = self.get_event_method()
        method._raw_args.add_get_vars(self.get_event_args())
        user = CLI.get_current_user()
        server = user.get_server()
        channel = server.get_or_create_channel(user.gdo_val('user_name'))
        method.env_user(user, True)
        method.env_server(server)
        method.execute()

    async def execute_dog(self):
        method = self.get_event_method()
        if args:= self.get_event_args():
            method._raw_args.add_cli_line(args)
        gdt = method.gdo_execute()
        while iscoroutine(gdt):
            gdt = await gdt
        return gdt

    async def execute_web(self):
        from gdo.core.connector.Web import Web
        from gdo.core.GDO_User import GDO_User
        method = self.get_event_method()
        if args:= self.get_event_args():
            method._raw_args.add_cli_line(args)
        method.env_server(Web.get_server())
        method.env_user(GDO_User.system(), True)
        method.env_channel(Web.get_public_channel())
        Application.get_page()._top_bar.add_field(await method.execute())
