class ConsumeResponse:

    def __init__(self, success: bool, data: dict):
        self.success = success

        if self.success:
            self.data = data[0]
        else:
            self.error = data["error_message"]

    def __repr__(self):
        if self.success:
            return f"Success - {abs(int(self.data['amount']))} consumed"
        else:
            return f"Failed - {self.error}"
