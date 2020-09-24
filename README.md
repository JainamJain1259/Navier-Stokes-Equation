# Navier-Stokes-Equation
Discretized Navier Stokes Equation and solved Flow inside a lid driven cavity using Finite Volume Menthod

# Question:
By employing ﬁnite volume method, discretize the Navier-Stokes equations to solve ﬂow within the lid-driven cavity at a Reynolds number of 100 with uniform meshing. Write a computer program to solve discretized equations. Use central diﬀerence method for discretization of convective terms. You may employ any method of your choice (SIMPLE, SIMPLER, or fractional-step method) to get the steady state solution. Solve the resulting equations using Gauss-Seidel method. Compare your results with those presented in Ghia et. al. (1982). Submit a report containing the details of discretization and the results. The geometry and boundary conditions are shown in ﬁgure 1. As presented in ﬁgure 2,
u− along Y Y and v− along XX should be presented in your report. Lines XX and Y Y are illustrated in ﬁgure 1. Reference values are given in Tables 1 and 2 of the reference paper. Use 64 × 64 grid to discretize the domain.
![Screenshot (7)](https://user-images.githubusercontent.com/69717816/94141060-d1ad6d80-fe89-11ea-8d8f-2731f003489e.png)

These are optional tasks but fetch you additional points:
- Use firrst order upwind for convective terms, and demonstrate the effect of artificial diffusion.
- Demonstrate that at a suﬃciently large P e number central diﬀerencing scheme results in unphys-ical oscillations, while upwind scheme provides a smooth solution.
- Implement SOR to solve the linear system of equations, and demonstrate the computational speedup for Reynolds number = 100 for relaxation factor ω ∈ [1,2] with increment of 0.1.
- Compare results for Reynolds number of 1000 and above.
- Plot streamlines within the cavity




