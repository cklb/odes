# Authors: B. Malengier 
"""
This example shows how to solve the planar pendulum in full coordinate space.
This results in a dae system with one algebraic equation. 

The problem is easily stated: a pendulum must move on a circle with radius 1, 
it has a mass m, and gravitational accelleration is g. 
The Lagragian is L = 1/2 m (u^2 + v^2) - m g y,
with constraint: x^2+y^2 = 1. 

Adding a Lagrange multiplier \lambda, we arrive at the Euler Lagrange 
differential equations for the problem:

\dot{x} = u
\dot{y} = v
\dot{u} = \lambda x/m
\dot{v} = \lambda y/m - g

and \lambda must be such that the constraint is satisfied:
x^2+y^2 = 1

DASPK cannot solve the above. Hence we derive a different constraint that
contains more of the unknowns, as well as \lambda. 

Derivation to time of the constraint gives a new constraint:
x u + y v =0

Derivating a second time to time gives us:
u^2 + v^2 + x \dot{u} + y \dot{v} = 0
which can be written with the known form of \dot{u}, \dot{v} as
u^2 + v^2 + \labmda l^2/m - g y = 0

This last expression will be used to find the solution to the planar 
pendulum problem. 

The algorithm first needs to find initial conditions for the derivatives,
then it solves the problme at hand. We take g=1, m=1

"""
from numpy import (arange, zeros, array, sin)
from scikits.odes.sundials.common_defs import ResFunction
import numpy as np
from scikits.odes.sundials import ida
import matplotlib.pyplot as plt

def draw_graphs(fignum, t, x, y):
    plt.figure(fignum)
    plt.subplot(211)
    plt.scatter(x, y)
    plt.xlabel('x coordinate')
    plt.ylabel('y coordinate')
    plt.axis('equal')
    plt.subplot(212)
    plt.plot(t, x, 'b', label='x coordinate')
    plt.plot(t, y, 'k', label='y coordinate')
    plt.legend()
    plt.ylabel('Coordinate')
    plt.xlabel('Time')
    plt.show()
    
class oscres(ResFunction):
    def evaluate(self, t, x, xdot, result, userdata):
        g=1
        result[0]=x[2]-xdot[0]
        result[1]=x[3]-xdot[1]
        result[2]=-xdot[2]-x[4]*x[0]
        result[3]=-xdot[3]-x[4]*x[1]-g
        #tmp[4]=x[0]*x[0]+x[1]*x[1]-1
        #tmp[4]=x[0]*x[2]+x[1]*x[3]
        result[4] = x[2]**2 + x[3]**2 \
                    - (x[0]**2 + x[1]**2)*x[4] - x[1] * g
        return 0
        
res=oscres()        

class SimpleOscillator():
    stop_t  = arange(.0,5,0.2,dtype=np.float)
    theta= 3.14/3 #starting angle
    x0=sin(theta)
    y0=-(1-x0**2)**.5

    g=1

    lambdaval = 0.1
    z0 =  array([x0, y0, 0., 0., lambdaval], np.float) 
    zprime0 = array([0., 0., -lambdaval*x0, -lambdaval*y0-g, -g], np.float)
    
    

problem = SimpleOscillator()
time = problem.stop_t
nr = len(time)

# Variant 1: Solving the problem with the 'run_solver' method
solver=ida.IDA(res,
               compute_initcond='yp0',               
               first_step=1e-18,
               atol=1e-6,rtol=1e-6,
               algebraic_vars_idx=[4])

# strip unneeded return values from run_solver
_flag, t1, y1 = solver.run_solver(time, problem.z0, problem.zprime0)[:3]


xt = y1[:, 0]
yt = y1[:, 1]

draw_graphs(1, t1, xt, yt)

# Variant 2: Solving the problem with the more versatile (but slower) method 'step'
problem.x0 = problem.x0 * 2
problem.y0 = problem.y0 * 2
problem.z0 =  array([problem.x0, problem.y0, 0., 0., problem.lambdaval], np.float)

y2 = np.empty([nr, len(problem.z0)], float)
# options for solver remain the same
# solver.set_options(...)
solver.init_step(time[0], problem.z0, problem.zprime0)
y2[0, :] = problem.z0
for i in range(len(time))[1:]:
    solver.step(time[i], y2[i, :])

xt = y2[:, 0]
yt = y2[:, 1]

draw_graphs(2, time, xt, yt)