#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File (Python):  'pairwise_registration.py'
author:         Tanguy Racine
date:           2025

Python implementation of Least squares fitting of 2 3D point sets (Arun et al., 1987)
"""

    
import numpy as np

def pairwise_registration(p1_t, p2_t , verbose : str = False, atol = 1e-1) -> dict:
    """
    Function to find the rotation and translation matrices for the rigid registration of point clouds.
    This  minimises the vector N for: 

    P2 = RP1 + t1.T
    P2 and P1 are 3 x N matrices representing two sets of N points (P2: targets, P1:to be registered). 
    R is the rotation matrix. 
    t is a translation vector. 

    ----------
    
    arguments:

    p1_t : an N x 3 matrix of reference point coordinates 
    p2_t : an N x 3 matrix of target point coordinates
    atol : tolerance for the distance of references to targets given the transformation

    ----------
    
    returns:

    result : the target point coordinates newly registered using the rotation and translation matrices. 
    R : the rotation matrix. 
    t : the translation vector. 
    """
    
    p1 = p1_t.T
    p2 = p2_t.T

    #Calculate centroids
    p1_c = np.mean(p1, axis = 1).reshape((-1,1)) #If you don't put reshape then the outcome is 1D with no rows/colums and is interpeted as rowvector in next minus operation, while it should be a column vector
    p2_c = np.mean(p2, axis = 1).reshape((-1,1))

    if verbose == True:
        print("centroids:\n")
        print("to be aligned:\n", p1_c)
        print("reference cloud:\n", p2_c)
        
    #Subtract centroids
    q1 = p1 - p1_c
    q2 = p2 - p2_c

    #Calculate covariance matrix
    H = q1 @ q2.T

    if verbose == True:
        print("covariance matrix H:\n", H)


    #Calculate singular value decomposition (SVD)
    U, X, V_t = np.linalg.svd(H) #the SVD of linalg gives you Vt

    if verbose == True:
        print("SVD of H:\n", V_t)
        print("X:\n", X)
        
    #Calculate rotation matrix
    R = V_t.T @ U.T

    if verbose == True:
        print("Rotation matrix:\n", R)
        
    assert np.allclose(np.linalg.det(R), 1.0), "Rotation matrix of N-point registration not 1, see paper Arun et al."

    #Calculate translation matrix
    T = p2_c - R @ p1_c
    
    if verbose == True:
        print("Translation matrix:\n", T)
    
    #Check result
    p1_prime = T + R @ p1

    if np.allclose(p1_prime,p2,atol=atol):
        print(f"mean residual errors are within tolerance of {atol}!")
    else:
        print(f"mean residual errors are above tolerance of {atol}!")

    result = {"P1_prime": p1_prime, # transformed source points
           "R": R, # rotation matrix
           "T": T} # translation vector
    return result