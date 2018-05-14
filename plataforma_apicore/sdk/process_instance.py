from sdk.apicore import ApiCore
import log

class ProcessInstance(ApiCore):

    def __init__(self):
        super().__init__()

    def get_processes_after(self, date, instance_id):
        params = {
            "filter":"executedAfter",
            "systemId": self.system_id(),
            "date": date.replace(tzinfo=None).isoformat("T"),
            "instanceId": instance_id
        }
        return self.get("processInstance", params)
