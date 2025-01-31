import numpy as np
import numpy.linalg as la

from pymanopt.manifolds.product import _ProductTangentVector

def smooth_l1(x, eps):
    with np.errstate(over='ignore'):
        res = eps * np.log(np.cosh(x/eps))
    ### fix eventual inf errors as best as possible
    if np.isscalar(res) and np.isinf(res):
        res = np.abs(x)
    else:
        ix = np.isinf(res)
        res[ix] = np.abs(x[ix])
    return res

def smooth_l1_deriv(x, eps):
    return np.tanh(x/eps)

def smooth_relu(x, eps):
    res = eps * np.log(1+np.exp(x/eps))
    ### fix eventual inf errors as best as possible
    if np.isscalar(res) and np.isinf(res):
        res = x
    else:
        ix = np.isinf(res)
        res[ix] = x[ix]
    return res

def smooth_relu_deriv(x, eps):
    res = np.exp(x/eps) / (1 + np.exp(x/eps))
    if np.isscalar(res) and np.isnan(res):
        res = 1
    else:
        res[np.isnan(res)] = 1 
    return res

def sparse_SPD_cost(R, h):
	p,_ = R.shape
	iR = la.inv(R)
	A = h(iR)
	return np.sum(A[np.triu_indices(p,k=1)]) + np.sum(A[np.tril_indices(p,k=-1)])

def sparse_SPD_egrad(R, dh):
    p,_ = R.shape
    iR = la.inv(R)
    ixu = np.triu_indices(p,k=1)
    ixl = np.tril_indices(p,k=-1)
    egrad = np.zeros((p,p))
    egrad[ixu] = dh(iR[ixu])
    egrad[ixl] = dh(iR[ixl])
    return -iR @ egrad @ iR
	
def sparse_SPD_rgrad(R, dh):
    p,_ = R.shape
    iR = la.inv(R)
    ixu = np.triu_indices(p,k=1)
    ixl = np.tril_indices(p,k=-1)
    grad = np.zeros((p,p))
    grad[ixu] = dh(iR[ixu])
    grad[ixl] = dh(iR[ixl])
    return -grad

def sparse_FactorLRpart_cost(theta, h):
    iS = la.inv(theta[1])
    iH = theta[0] @ iS @ theta[0].T
    p,_ = iH.shape
    A = h(iH)
    return np.sum(A[np.triu_indices(p,k=1)]) + np.sum(A[np.tril_indices(p,k=-1)])

def sparse_FactorLRpart_egrad(theta, dh):
    iS = la.inv(theta[1])
    iH = theta[0] @ iS @ theta[0].T
    p,_ = iH.shape
    ixu = np.triu_indices(p,k=1)
    ixl = np.tril_indices(p,k=-1)
    grad = np.zeros((p,p))
    grad[ixu] = dh(iH[ixu])
    grad[ixl] = dh(iH[ixl])
    return _ProductTangentVector([ 2 * grad @ theta[0] @ iS, - iS @ theta[0].T @ grad @ theta[0] @ iS, np.zeros(p) ])


