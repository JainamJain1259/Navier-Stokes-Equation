
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
#--------------Diffusive coefficients----------------#
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
 #--------Convective Coefficients----------#
                Fe = (dy/2)*(u[i+1][j] + u[i][j])
                Fw = (dy/2)*(u[i][j] + u[i-1][j])
                Fn = (dx/2)*(v[i][j] + v[i+1][j])
                Fs = (dx/2)*(v[i][j-1] + v[i+1][j-1])

                aE = De + max(-Fe,0)
                aW = Dw + max(Fw,0)
                aN = Dn + max(-Fn,0)
                aS = Ds + max(Fs,0)
                aP = De + max(Fe,0) + Dw + max(-Fw,0) + Dn + max(Fn,0) + Ds + max(-Fs,0)
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
#--------Diffussion Coefficients----------#
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
#---------------Convective Coefficients-------------#
                Fe = (dy/2)*(u[i][j+1] + u[i][j])
                Fw = (dy/2)*(u[i-1][j+1] + u[i-1][j])
                Fn = (dx/2)*(v[i][j+1] + v[i][j])
                Fs = (dx/2)*(v[i][j-1] + v[i][j])

                aE = De + max(-Fe,0)
                aW = Dw + max(Fw,0)
                aN = Dn + max(-Fn,0)
                aS = Ds + max(Fs,0)
                aP = De + max(Fe,0) + Dw + max(-Fw,0) + Dn + max(Fn,0) + Ds + max(-Fs,0)
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
  miter = 100                            # Maximum number of iterations for convergence of P_error
  
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

def plot(u,v,nx,ny,Re):
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    uu = np.zeros((nx, ny))
    vv = np.zeros((nx, ny))
    for i in range(1, nx):
        for j in range(1, ny):
            uu[i - 1, j - 1] = u[i, j + 1]
            vv[i - 1, j - 1] = v[i + 1, j]

#---------------t variable is used to store data at each combination of grids i.e 64*64, 44*44, 20*20 and 12*12----------------#
#    t = np.zeros(ny) 
#    t[:] = uu[32,:]
#    print(t)
#    print(y)


    plt.axis([-0.2, 1.2, 0, 1.2])
    plt.streamplot(x, y, uu.transpose(), vv.transpose())
    plt.title('%d by %d velocity streamline Re= %d' % (nx, ny, Re))
    plt.show()


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

#---------------Data used to plot artificial diffusion at each combination of grid points--------------#

    #plt.plot([0.0, 0.01587302,0.03174603,0.04761905,0.06349206,0.07936508,0.0952381,0.11111111,0.12698413,0.14285714, 0.15873016, 0.17460317,0.19047619, 0.20634921, 0.22222222, 0.23809524, 0.25396825, 0.26984127, 0.28571429, 0.3015873,  0.31746032, 0.33333333, 0.34920635, 0.36507937,0.38095238, 0.3968254,  0.41269841, 0.42857143, 0.44444444, 0.46031746, 0.47619048, 0.49206349, 0.50793651, 0.52380952, 0.53968254, 0.55555556,0.57142857, 0.58730159, 0.6031746,  0.61904762 ,0.63492063, 0.65079365,0.66666667 ,0.68253968 ,0.6984127  ,0.71428571 ,0.73015873, 0.74603175,0.76190476, 0.77777778 ,0.79365079 ,0.80952381 ,0.82539683 ,0.84126984,0.85714286, 0.87301587 ,0.88888889 ,0.9047619 , 0.92063492 ,0.93650794,0.95238095, 0.96825397 ,0.98412698],[-0.02083186, -0.03025627 ,-0.03915098, -0.04759958, -0.05567572, -0.06344414,-0.07096137 ,-0.07827626 ,-0.08543017 ,-0.09245713, -0.09938375 ,-0.10622916,-0.11300478 ,-0.11971415 ,-0.1263527 , -0.13290768, -0.13935851 ,-0.14567336,-0.15181409 ,-0.15773398 ,-0.16337833 ,-0.16868478, -0.17358406 ,-0.17800041,-0.1818512  ,-0.18505231 ,-0.18751747 ,-0.18915872, -0.189889   ,-0.18962434,-0.18828644 ,-0.18580367 ,-0.18211303 ,-0.17716273, -0.17091297 ,-0.16333661,-0.15441987 ,-0.14416262 ,-0.13257648 ,-0.1196825 , -0.10550824 ,-0.09008342,-0.07343363 ,-0.05557286 ,-0.03649481 ,-0.01616275,  0.0055024  , 0.02863869,0.05347414 , 0.08032181 , 0.10959359 , 0.14181254,  0.1776213   ,0.2177827,0.2631672  , 0.31471981 , 0.37339752  ,0.4400673 ,  0.51535681  ,0.59945619,0.69188383 , 0.79125407,  0.89511945],label = '64*64', color ='red')
    #plt.plot([0.0 , 0.02325581, 0.04651163, 0.06976744, 0.09302326 ,0.11627907,0.13953488 ,0.1627907 , 0.18604651 ,0.20930233 ,0.23255814 ,0.25581395,0.27906977 ,0.30232558, 0.3255814  ,0.34883721 ,0.37209302 ,0.39534884,0.41860465 ,0.44186047, 0.46511628 ,0.48837209 ,0.51162791 ,0.53488372,0.55813953 ,0.58139535, 0.60465116 ,0.62790698 ,0.65116279 ,0.6744186,0.69767442 ,0.72093023, 0.74418605 ,0.76744186 ,0.79069767 ,0.81395349, 0.8372093  ,0.86046512, 0.88372093 ,0.90697674 ,0.93023256 ,0.95348837, 0.97674419 ],[-2.90337404e-02, -4.16354167e-02, -5.33063544e-02, -6.42529555e-02,-7.46454230e-02, -8.46206737e-02, -9.42838563e-02, -1.03708836e-01,-1.12937982e-01, -1.21981581e-01, -1.30817187e-01, -1.39389366e-01,-1.47611066e-01, -1.55355353e-01, -1.62467974e-01, -1.68767743e-01,-1.74049963e-01, -1.78089050e-01, -1.80647183e-01, -1.81479019e-01,-1.80350042e-01, -1.77043002e-01, -1.71361393e-01, -1.63146835e-01,-1.52289751e-01, -1.38725242e-01, -1.22431579e-01, -1.03428147e-01,-8.17590800e-02, -5.74540466e-02, -3.04868370e-02, -7.22809076e-04, 3.21497887e-02,  6.88041699e-02,  1.10268899e-01,  1.57998968e-01,2.13926461e-01,  2.80450307e-01,  3.60296706e-01,  4.56146613e-01,5.69904627e-01,  7.01528078e-01,  8.47554982e-01],label = '44*44', color ='blue')
    #plt.plot([0.0 , 0.05263158, 0.10526316, 0.15789474 ,0.21052632, 0.26315789, 0.31578947 ,0.36842105 ,0.42105263 ,0.47368421 ,0.52631579 ,0.57894737,0.63157895 ,0.68421053 ,0.73684211 ,0.78947368 ,0.84210526 ,0.89473684,0.94736842],[-0.05384999, -0.07396894, -0.09168135, -0.10779469, -0.1225427 , -0.13561262,-0.14618086, -0.15297053, -0.15430134, -0.14832039, -0.13318589, -0.10722078,-0.06901078, -0.01757369,  0.04851354,  0.13524747,  0.25521623,  0.42848375,0.6774794 ] ,label = '20*20', color ='green')  
    #plt.plot([0.0,0.09090909, 0.18181818, 0.27272727, 0.36363636 ,0.45454545,0.54545455, 0.63636364, 0.72727273 ,0.81818182, 0.9090909 ],[-0.07291517 ,-0.09519314 ,-0.11282427 ,-0.12524748 ,-0.12924254, -0.11940658,-0.08827853 ,-0.0276962  , 0.07056401 , 0.23045758, 0.51314063],label = '12*12', color = 'black')
    #plt.xlabel('y/L')
    #plt.ylabel('velocity(u/U0)')
    #plt.legend()
    #plt.show()




#--------------------Main Function-----------------#                                   
import numpy as np
import math as m
import matplotlib.pyplot as plt
import sys

nx     = 64         # Number of Control volumes in x direction
ny     = 64         # Number of control volumes in y direction
Re     = 1000       # Reynolds Number
iter   = 0.0        # Iteration count
U0     = 1.0        # Lid velocity
L      = 1.0        # Length of box in x direction
H      = 1.0        # Heigth of box in y direction
del_x  = L/nx       # Distance between two consecutive mesh points in X direction
del_y  = H/ny       # Distance between two consecutive mesh points in Y direction
alphaP = 0.4        # Relaxation Factor for Pressure
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

u_old[0, :]  = 0                     # Left Face 
u_old[-1, :] = 0                     # Right Face 
u_old[:, 0]  = 0                     # Bottom Face 
u_old[:, -1] = U0                    # Top Face
v_old[0, :]  = 0                     # Left Face
v_old[-1, :] = 0                     # Right Face
v_old[:, 0]  = 0                     # Bottom Face
v_old[:, -1] = 0                     # Top Face

plot(u,v,nx,ny,Re)

print("Total Number of iterations for convergence = ", iter)

