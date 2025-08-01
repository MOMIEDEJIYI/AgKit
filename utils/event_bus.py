# event_bus.py
class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_name: str, callback):
        """订阅事件"""
        if not callable(callback):
            raise ValueError("callback 必须是可调用对象")
        self._subscribers.setdefault(event_name, []).append(callback)

    def unsubscribe(self, event_name: str, callback):
        """取消订阅事件"""
        if event_name in self._subscribers:
            self._subscribers[event_name] = [
                cb for cb in self._subscribers[event_name] if cb != callback
            ]

    def publish(self, event_name: str, *args, **kwargs):
        """发布事件"""
        for cb in self._subscribers.get(event_name, []):
            cb(*args, **kwargs)


# 单例，全局使用
event_bus = EventBus()
