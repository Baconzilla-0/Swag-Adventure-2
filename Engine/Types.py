class IntConstrained:
    def __init__(self, Value, Min, Max):
        self.Value = Value
        self.Min = Min
        self.Max = Max
    def Modify(self, Amount):
        Predicted = self.Value + Amount

        if Predicted <= self.Max and Predicted >= self.Min:
            self.Value = Predicted