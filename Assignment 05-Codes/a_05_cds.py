
#------------Error between old value and new value--------------#
def error(u,u_old,v,v_old,nx,ny):
    udiff = np.zeros((nx,ny))
    vdiff = np.zeros((nx,ny))
    for i in range(0,nx):
        for j in range(0,ny):
            udiff[i,j] = abs(u[i,j] - u_old[i, j])
            vdiff[i,j] = abs(v[i,j] - v_old[i, j])
    umax = max(map(max, udiff))
    vmax = max(map(max, vdiff))
    maxerror = max(umax, vmax)
    return maxerror

#------------Solving x momentum equation------------------#
def u_momentum(nx,ny,dx,dy,b,u,v,P,U0,alpha):
    d_u    = np.zeros((nx+1,ny+2))     # Presure correction coefficients
    u_star = np.zeros((nx+1,ny+2))     # Intermediate x-velocity array between (k)th and (k+1)th iteration
    usOld  = np.zeros((nx+1,ny+2))     # Used to converge the u_star obtained using Guass-Siedel method
    merr   = 0.001                     # Error for convergence of u_star
    miter  = 100                       # Maximum number of iterations for convergence of u_star

#--------Transfering the old solution to u_star----------#
    for i in range(0,nx+1):
        for j in range(0,ny+2):
            u_star[i,j] = u[i,j]
#--------Diffusive Coefficients----------#
    De  = b*dy / dx  
    Dw  = b*dy / dx 
    Dn  = b*dx / dy 
    Ds  = b*dx / dy

    m = 0
    err = 1
#--------Convergence loop of u_star-----------#
    while(err > merr):
        m = m + 1

        for i in range(1,nx):
            for j in range(1,ny+1):
 #--------------Convective coefficients----------------#
                Fe = (dy/2)*(u[i+1][j] + u[i][j])
                Fw = (dy/2)*(u[i][j] + u[i-1][j])
                Fn = (dx/2)*(v[i][j] + v[i+1][j])
                Fs = (dx/2)*(v[i][j-1] + v[i+1][j-1])

#---------------Neighbour Coefficients---------------#
                aE = De - (Fe/2)
                aW = Dw + (Fw/2)
                aN = Dn - (Fn/2)
                aS = Ds + (Fs/2)
                aP = De + Fe + Dw - Fw + Dn + Fn + Ds - Fs
                pressure_term = (P[i][j] - P[i+1][j])*dy

#------------Discretized x-momentum equation solved using Gauss-Siedel Method--------------#
                u_star[i,j] = (alpha/aP) * (aE*u_star[i+1][j] + aW*u_star[i-1][j] + aN*u_star[i][j+1] + aS*u_star[i][j-1] + pressure_term ) + (1-alpha)*u[i][j]
                d_u[i,j] = alpha*dy/aP
        
        if m > 1:
          err = error(u_star,usOld,u_star,usOld,nx,ny)

        for i in range(1,nx):
            for j in range(1,ny+1):
                usOld[i, j] = u_star[i, j]

        if m > miter:
            break

    return [u_star,d_u] 

#------------Solving y momentum equation------------------#
def v_momentum(x,y,dx,dy,b,v,u,P,alpha):
  
    d_v    = np.zeros((nx+2,ny+1))     # Presure correction coefficients
    v_star = np.zeros((nx+2,ny+1))     # Intermediate y-velocity array between (k)th and (k+1)th iteration
    vsOld  = np.zeros((nx+2,ny+1))     # Used to converge the v_star obtained using Guass-Siedel method
    miter  = 100                       # Maximum number of iterations for convergence of v_star
    merr  = 0.001                      # Error for convergence of v_star

#--------Transfering the old solution to v_star----------#
    for i in range(0,nx+2):
        for j in range(0,ny+1):
            v_star[i,j] = v[i,j]
#--------Diffusive Coefficients----------#
    De  = b*dy / dx  
    Dw  = b*dy / dx 
    Dn  = b*dx / dy 
    Ds  = b*dx / dy

    m = 0
    err = 1
#--------Convergence loop of v_star-----------#
    while(err > merr):
        m = m + 1

        for i in range(1,nx+1):
            for j in range(1,ny):
#---------------Convective coefficients---------------#
                Fe = (dy/2)*(u[i][j+1] + u[i][j])
                Fw = (dy/2)*(u[i-1][j+1] + u[i-1][j])
                Fn = (dx/2)*(v[i][j+1] + v[i][j])
                Fs = (dx/2)*(v[i][j-1] + v[i][j])

#---------------Neghbour Coefficients-------------#
                aE = De - (Fe/2)
                aW = Dw + (Fw/2)
                aN = Dn - (Fn/2)
                aS = Ds + (Fs/2)
                aP = De + Fe + Dw - Fw + Dn + Fn + Ds - Fs
                pressure_term = (P[i][j] - P[i][j+1])*dy

#------------Discretized y-momentum equation solved using Gauss-Siedel Method--------------#
                v_star[i,j] = (alpha/aP) * (aE*v_star[i+1][j] + aW*v_star[i-1][j] + aN*v_star[i][j+1] + aS*v_star[i][j-1] + pressure_term ) + (1-alpha)*v_old[i][j]
                d_v[i,j] = alpha*dy/aP
      
        if m > 1:
            err = error(v_star,vsOld,v_star,vsOld,nx,ny)
        for i in range(1,nx):
            for j in range(1,ny+1):
                vsOld[i, j] = v_star[i, j]
        if m > miter:
            break

    return [v_star,d_v]

#-----------------Pressure correction function-----------------#
def pressure(nx,ny,dx,dy,b,u,v,d_u,d_v,iter):

  P_error = np.zeros((nx+2,ny+2))         # Stores pressure correction values P(tilda)
  Pp_error = np.zeros((nx+2,ny+2))        # Used for convergence of pressure correction values between (k)th iteration and (k+1)th iteration
  merr = 0.001                            # Error for convergence of P_error
  miter = 100                             # Maximum number of iterations for convergence of P_error
  
  err = 1
  m = 0
#--------Convergence loop of P_error-----------#
  while( err > merr):
      m = m + 1

      for i in range(1,nx + 1):
          for j in range(1,ny + 1):

#-------------Coefficients of neighbouring nodes-----------#          
              dE = d_u[i][j]*dy
              dW = d_u[i-1][j]*dy
              dN = d_v[j][j]*dx
              dS = d_v[i][j-1]*dx
              dP = dE + dW + dN + dS
              rhs = (u[i][j] - u[i-1][j])*dy + (v[i][j] - v[i][j-1])*dx
#-------------For reference the initial conditions are set to be zero--------------#
              if iter == 1:
                  dP = 1
                  dE = 0
                  dW = 0
                  dS = 0
                  dN = 0
                  rhs = 0
#---------------Pressure Correction equation solved using Guass-Siedel method-------------#
              P_error[i,j] = (dE*P_error[i+1][j] + dW*P_error[i-1][j] + dN*P_error[i][j+1] + dS*P_error[i][j-1] - rhs)/dP
      
      if m > 1:
          err = error(P_error, Pp_error, P_error, Pp_error, nx, ny)
      for i in range(1, nx + 1):
          for j in range(1, ny + 1): 
            Pp_error[i,j] = P_error[i,j]
      if m > miter:
          break
  return(P_error)

#--------------Calculation of u(k+1), v(k+1) and P(k+1)----------------#
def update_velocity(nx,ny,u,v,d_u,d_v,P,P_old):

    u_new   = np.zeros((nx+1,ny+2))
    v_new   = np.zeros((nx+2,ny+1))
    P_new   = np.zeros((nx+2,ny+2))
    u_error = np.zeros((nx+1,ny+2))
    v_error = np.zeros((nx+2,ny+1))  

    for i in range(1,nx+1):
        for j in range(1,ny+1):
            P_new[i,j] = P_old[i][j] + alphaP*P[i][j]

    for i in range(1,nx):
        for j in range(1,ny+1):
            u_error[i,j] = (P[i][j] - P[i+1][j])*d_u[i][j]
            u_new[i,j] = u[i][j] + u_error[i][j]
    
    for i in range(1,nx + 1):
        for j in range(1,ny):
          v_error[i,j] = (P[i][j] - P[i][j+1])*d_v[i][j]
          v_new[i,j] = v[i][j] + v_error[i][j]
    
    return[u_error,v_error,u_new,v_new,P_new]

def plot(u,v,nx,ny):
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    uu = np.zeros((nx, ny))
    vv = np.zeros((nx, ny))
    for i in range(1, nx):
        for j in range(1, ny):
            uu[i - 1, j - 1] = u[i, j + 1]
            vv[i - 1, j - 1] = v[i + 1, j]
#--------------Streamline Plot----------------#            
    plt.axis([-0.2, 1.2, 0, 1.2])
    plt.streamplot(x, y, uu.transpose(), vv.transpose())
    plt.title('%d by %d velocity streamline Re= %d' % (nx, ny, Re))
    plt.show()

#------------u/U0 vs y/H plot----------------#
    y = np.linspace(0, 1, ny + 2)
    plt.plot(y, u[32,:],label= "Present",color = "blue")
    plt.axis([0, 1, min(u[32,:]), max(u[32,:])])
    if Re == 100:
      plt.plot([0,0.0547,0.0625,0.0703,0.1016,0.1719,0.2813,0.4531,0.5000,0.6172,0.7344,0.8516,0.9531,0.9609,0.9688,0.9766,1.000],[0,-0.03717,-0.04192,-0.04775,-0.06434,-0.10150,-0.15662,-0.21090,-0.20581,-0.13641,0.00332,0.23151,0.68717,0.73722,0.78871,0.84123,1.000],'-o',label="Ghia et. al.",c='red')
    elif Re == 1000:
      plt.plot( [0.00, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813, 0.4531 ,0.5, 0.6172, 0.7344, 0.8516 ,0.9531 ,0.9609 ,0.9688, 0.9766, 1],[0,-0.18109,-0.20196,-0.22220,-0.29730,-0.38298,-0.27805,-0.10648,-0.06080,0.05702,0.18719,0.33304,0.46604,0.51117,0.57492,0.65928,1],'-o',label="Ghia et. al.",c='red')
    elif Re == 3200:
      plt.plot([0.00, 0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813, 0.4531 ,0.5, 0.6172, 0.7344, 0.8516 ,0.9531 ,0.9609 ,0.9688, 0.9766, 1],[0,-0.32407,-0.35344,-0.37827,-0.41933,-0.34323,-0.24427,-0.86636,-0.04272,0.07156,0.19791,0.34682,0.46101,0.46547,0.48296,0.53236,1],'-o',label="Ghia et. al.",c='red')
    plt.title('%d by %d Graph u-vel through vertical center line Re= %d' % (nx, ny, Re))
    plt.xlabel('y/H ')
    plt.ylabel('velocity(u/U0)')
    plt.legend()
    plt.show()

#-----------v/U0 vs x/L plot-----------------#    
    x = np.linspace(0, 1, nx + 2)
    plt.plot(x, v[:, 32],label= "Present",color = "blue")
    plt.axis([0, 1, min(v[:, 32]), max(v[:, 32])])
    if Re == 100:
      plt.plot([0,0.0625,0.0703,0.0781,0.0938,0.1563,0.2266,0.2344,0.5,0.8047,0.8594,0.9063,0.9453,0.9531,0.9609,0.9688,1],[0,0.09233,0.10091,0.10890,0.12317,0.16077,0.17507,0.17527,0.05454,-0.24533,-0.22445,-0.16914,-0.10313,-0.08864,-0.07391,-0.05906,0],'-o',label="Ghia et. al.",c='red')
    elif Re ==1000:
      plt.plot( [0.00, 0.0625, 0.0703, 0.0781, 0.0938, 0.1563, 0.2266, 0.2344 ,0.5, 0.8047, 0.8594, 0.9063 ,0.9453 ,0.9531 ,0.9609, 0.9688, 1],[0,0.27485,0.29012,0.30353,0.32627,0.37095,0.33075,0.32235,0.022526,-0.31966,-0.42665,-0.51550,-0.39188,-0.33714,-0.27669,-0.21388,0],'-o',label="Ghia et. al.",c='red')
    elif Re== 3200:
      plt.plot([0,0.0625,0.0703,0.0781,0.0938,0.1563,0.2266,0.2344,0.5,0.8047,0.8594,0.9063,0.9453,0.9531,0.9609,0.9688,1],[0,0.39560,0.40917,0.41906,0.42768,0.37119,0.29030,0.28188,0.00999,-0.31184,-0.37401,-0.44307,-0.54053,-0.52357,-0.47425,-0.39017,0],'-o',label="Ghia et. al.",c='red')
    plt.title('%d by %d Graph v-vel through horizontal center line Re= %d' % (nx, ny, Re))
    plt.xlabel('x/L')
    plt.ylabel('velocity(v/U0)')
    plt.legend()
    plt.show()
    
#--------------------Main Function-----------------#                                   
import numpy as np
import math as m
import matplotlib.pyplot as plt
import sys

nx     = 64         # Number of Control volumes in x direction
ny     = 64         # Number of control volumes in y direction
Re     = 1000        # Reynolds Number
iter   = 0.0        # Iteration count
U0     = 1.0        # Lid velocity
L      = 1.0        # Length of box in x direction
H      = 1.0        # Heigth of box in y direction
del_x  = L/nx       # Distance between two consecutive mesh points in X direction
del_y  = H/ny       # Distance between two consecutive mesh points in Y direction
alphaP = 0.5        # Relaxation Factor for Pressure
alphaU = 0.7        # Relaxation factor for Velocities
tol    = 0.00001    # Error between (k)th iteration and (k+1)th iteration
b      = 1/Re

P_old   = np.zeros((nx+2,ny+2))   # Pressure at kth iteration
P_error = np.zeros((nx+2,ny+2))   # Pressure correction array
p       = np.zeros((nx+2,ny+2))   # Pressure at kth iteration

u_star = np.zeros((nx+1,ny+2))   # Intermediate x velocity between kth iteration and (k+1) th iteration
u_old  = np.zeros((nx+1,ny+2))   # x velocity at kth iteration
u      = np.zeros((nx+1,ny+2))   # x velocity at k+1 th iteration
d_u    = np.zeros((nx+1,ny+2))   # Presure correction coefficients

v_star = np.zeros((nx+2,ny+1))   # Intermediate y velocity between kth iteration and (k+1) th iteration
v_old  = np.zeros((nx+2,ny+1))   # y velocity at kth iteration
v      = np.zeros((nx+2,ny+1))   # y velocity at k+1 th iteration
d_v    = np.zeros((nx+2,ny+1))   # Presure correction coefficients

u_error = np.zeros((nx+1,ny+2))  # X-velocity correction
v_error = np.zeros((nx+2,ny+1))  # Y-velocity correction

while(True):

  iter = iter + 1
  # Boundary Conditions
  u_old[0, :]  = 0                     # Left Face 
  u_old[-1, :] = 0                     # Right Face 
  u_old[:, 0]  = 0                     # Bottom Face 
  u_old[:, -1] = U0                    # Top Face
  v_old[0, :]  = 0                     # Left Face
  v_old[-1, :] = 0                     # Right Face
  v_old[:, 0]  = 0                     # Bottom Face
  v_old[:, -1] = 0                     # Top Face
  p[0, :]      = p[1, :]               # Left Face
  p[-1, :]     = p[-2, :]              # Right Face  
  p[:, 0]      = p[:, 1]               # Bottom Face   
  p[:, -1]     = p[:, -2]              # Top Face

  [u_star,d_u] = u_momentum(nx,ny,del_x,del_y,b,u_old,v_old,P_old,U0,alphaU)
  [v_star,d_v] = v_momentum(nx,ny,del_x,del_y,b,v_old,u_old,P_old,alphaU)
  P_error = pressure(nx,ny,del_x,del_y,b,u_star,v_star,d_u,d_v,iter)
  [u_error,v_error,u,v,p] = update_velocity(nx,ny,u_star,v_star,d_u,d_v,P_error,P_old)

  norm = error(u,u_old,v,v_old,nx,ny)
  
  if norm < tol:
    break

  print(iter,norm)
  
  if norm > 2:
    print("Solution is diverged")
    break
  
  u_old[:,:] = u[:][:]
  v_old[:,:] = v[:][:]
  P_old[:,:] = p[:][:]

u[0, :]  = 0                     # Left Face 
u[-1, :] = 0                     # Right Face 
u[:, 0]  = 0                     # Bottom Face 
u[:, -1] = U0                    # Top Face
v[0, :]  = 0                     # Left Face
v[-1, :] = 0                     # Right Face
v[:, 0]  = 0                     # Bottom Face
v[:, -1] = 0                     # Top Face

plot(u,v,nx,ny,Re)

print("Total Number of iterations for convergence = ", iter)
