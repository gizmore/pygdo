class Events:
    _subscribers: dict[str, list[dict]]
    _timers: list[dict]

    def __init__(self):
        self._subscribers = {}
        self._timers = []

    def reset_all(self):
        self.reset_events()
        self.reset_timers()

    def reset_events(self):
        self._subscribers = {}

    def reset_timers(self):
        self._timers = []

    ##########
    # Events #
    ##########

    def subscribe(self, event_name: str, subscriber: callable):
        self.subscribe_times(event_name, subscriber, 2_000_000_000)

    def subscribe_once(self, event_name: str, subscriber: callable):
        self.subscribe_times(event_name, subscriber, 1)

    def subscribe_times(self, event_name: str, subscriber: callable, times: int):
        event_sub = {
            "count": times,
            "callback": subscriber,
        }
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(event_sub)

    def unsubscribe(self, event_name: str, subscriber: callable):
        if event_name in self._subscribers:
            self._subscribers[event_name] = [sub for sub in self._subscribers[event_name] if sub['callback'] != subscriber]
#            self._subscribers[event_name].remove(subscriber)

    def publish(self, event_name, *args, **kwargs):
        to_delete = []

        if event_name in self._subscribers:
            for subscriber in self._subscribers[event_name]:
                subscriber['callback'](*args, **kwargs)
                subscriber['count'] -= 1
                if subscriber['count'] == 0:
                    to_delete.append(subscriber['callback'])

        for callback in to_delete:
            self.unsubscribe(event_name, callback)

    #########
    # Timer #
    #########

    def add_timer(self, duration: float, callback: callable, repeat: int = 1):
        from gdo.base.Application import Application
        timer = {'duration': duration, 'callback': callback, 'repeat': repeat, 'next_run': Application.TIME + duration}
        self._timers.append(timer)

    def remove_timer(self, callback):
        self._timers = [timer for timer in self._timers if timer['callback'] != callback]

    def update_timers(self, current_time: float):
        expired_timers = []

        for timer in self._timers:
            if current_time >= timer['next_run']:
                timer['callback']()
                timer['repeat'] -= 1
                if timer['repeat'] > 0:
                    timer['next_run'] = current_time + timer['duration']
                else:
                    expired_timers.append(timer)

        for expired_timer in expired_timers:
            self._timers.remove(expired_timer)

    #############
    # Decorator #
    #############

