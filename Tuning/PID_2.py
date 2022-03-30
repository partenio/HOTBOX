import time


# cut the values to maintain the physical limits
def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class PID:

    # initialize the class
    def __init__(self, kp, ki, kd, target):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.target = target

    # variables declaration
        self.output_proportional = 0
        self.output_derivative = 0
        self.output_integral = 0
        self.delta_error = 0
        self.last_output = 0
        self.last_input = 0
        self.last_error = 0
        self.last_time = 0
        self.error = 0
        self.now = 0
        self.dt = 0

    def _proportional(self):
        self.output_proportional = self.kp * self.error

    def _derivative(self):
        self.output_derivative = -self.kd * (self.delta_error / self.dt)

    def _integral(self):
        self.output_integral += self.ki * self.error * self.dt
        self.output_integral = _clamp(self.output_integral, (0, 5))  # keep an eye in this _clamp function here

    def output(self, input_):
        self.error = self.target - input_
        self.delta_error = self.error - self.last_error
        self.now = time.time()

        # making sure dt is always positive and grater than 0
        if self.last_time > 0:
            self.dt = self.now - self.last_time
        else:
            self.dt = 1

        if self.dt <= 0:
            self.dt = 1

        # call the functions to execute the calculations
        self._proportional()
        self._derivative()
        self._integral()
        # output
        output = self.output_integral + self.output_derivative + self.output_proportional
        output = _clamp(output, (0, 5))
        # keep track of old values
        self.last_output = output
        self.last_input = input_
        self.last_time = self.now
        self.last_error = self.error
        return output
