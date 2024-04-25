class Events:
    _subscribers: dict
    _timers: list[dict]

    def __init__(self):
        self._subscribers = {}
        self._timers = []

    def subscribe(self, event_type: str, subscriber: callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(subscriber)

    def unsubscribe(self, event_type: str, subscriber: callable):
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(subscriber)

    def publish(self, event_type, *args, **kwargs):
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                subscriber(*args, **kwargs)

    #########
    # Timer #
    #########

    def add_timer(self, duration: float, callback: callable, repeat: bool = False):
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
                if timer['repeat']:
                    timer['next_run'] = current_time + timer['duration']
                else:
                    expired_timers.append(timer)

        for expired_timer in expired_timers:
            self._timers.remove(expired_timer)

