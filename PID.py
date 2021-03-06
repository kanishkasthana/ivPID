#!/usr/bin/python
#
# This file is part of IvPID.
# Copyright (C) 2015 Ivmech Mechatronics Ltd. <bilgi@ivmech.com>
#
# IvPID is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IvPID is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# title           :PID.py
# description     :python pid controller
# author          :Caner Durmusoglu
# date            :20151218
# version         :0.1
# notes           :
# python_version  :2.7
# ==============================================================================

"""Ivmech PID Controller is simple implementation of a Proportional-Integral-Derivative (PID) Controller in the Python Programming Language.
More information about PID Controller: http://en.wikipedia.org/wiki/PID_controller
"""
import time

class PID:
    """PID Controller
    """

    def __init__(self, P=0.2, I=0.0, D=0.0):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.flush=False
        self.flush_pressure=0.0
        self.clear()

    def clear(self):
        """Clears PID computations and coefficients"""
        self.sample_time = 0.00
        self.current_time = time.time()
        self.last_time = self.current_time
        self.windup_guard = 1000000.0 #Defining windup gaurd just to be sure things don't get out of control
        self.SetPoint = 0.0
        self.flush=False
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.int_error = 0.0
        self.windup_guard = 1000000.0

        self.output = 0.0
       
    def start_flush_at_pressure(self,pressure):
        """Variable to set when flushing a particular channel at the pressure specified"""
        self.flush=True
        self.flush_pressure=pressure
        
    def restart_flow(self,newSetpoint,newI,lastOutput):
        self.Ki=newI
        self.sample_time = 0.00
        self.current_time = time.time()
        self.last_time = self.current_time
        self.windup_guard = 1000000.0 #Defining windup gaurd just to be sure things don't get out of control
        self.flush=False
        self.flush_pressure=0.0
        self.PTerm = 0.0
        self.ITerm = lastOutput/self.Ki
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.int_error = 0.0
        self.windup_guard = 1000000.0

        self.output = lastOutput
        self.SetPoint = newSetpoint
       
        
        
    def stop_flush(self):
        """Stops flush and sets flush_pressure to 0.0"""
        self.flush=False
        self.flush_pressure=0.0
        self.SetPoint=0.0
        self.clear()

    def clearI(self):
        """Clears I term only"""
        self.ITerm = 0.0

    def update(self, feedback_value):
        """Calculates PID value for given reference feedback

        .. math::
            u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}

        .. figure:: images/pid_1.png
           :align:   center

           Test PID with Kp=1.2, Ki=1, Kd=0.001 (test_pid.py)

        """
        error = self.SetPoint - feedback_value

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        # Remember last time and last error for next calculation
        self.last_time = self.current_time
        self.last_error = error

        if (delta_time >= self.sample_time):
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time
           #Windup gaurd.
            if (self.ITerm < -self.windup_guard):
                self.ITerm = -self.windup_guard
            elif (self.ITerm > self.windup_guard):
                self.ITerm = self.windup_guard

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
        #Adding functionality for flushing     
        if self.flush is True:
            return(self.flush_pressure)
        else:
            return(self.output)

    def setTargetValue(self, targetValue):
        self.SetPoint = targetValue

    def setKp(self, proportional_gain):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
        self.Kd = derivative_gain

    def setWindup(self, windup):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    def getTargetValue(self):
        return(self.SetPoint)
    
    def getFlushValue(self):
        return(self.flush)

    def setSampleTime(self, sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time
