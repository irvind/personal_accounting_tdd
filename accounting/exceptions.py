class ExpstrError(Exception):
    def __init__(self, **kwargs):
        self.error_desc = kwargs
