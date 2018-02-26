"""Defines the GradientDescent class."""

import numbers

import numpy as np

from .base import Optimizer


class GradientDescent(Optimizer):
    """Unconstrained batch gradient descent with momentum."""

    def __init__(self, rate=0.1, momentum=0.0, nesterov=False, anneal=np.inf,
                 iterations=10000):
        """Initialize the parameters of a gradient descent object.

        Parameters
        ----------
        rate: float, optional
            Step size/learning rate. Must be positive.
        momentum: float, optional
            Momentum parameter. Must be positive.
        nesterov: bool
            If True, the update rule is Nesterov's accelerated gradient descent.
            If False, the update rule is vanilla gradient descent with momentum.
        anneal: float, optional
            Factor determining the annealing schedule of the learning rate. Must
            be positive. Smaller values lead to faster shrinking of the learning
            rate over time.
        iterations: int, optional
            Number of iterations of the algorithm to perform. Must be positive.
        """
        if not isinstance(rate, numbers.Real) or rate <= 0:
            raise TypeError("Parameter 'rate' must be a positive float")
        if not isinstance(momentum, numbers.Real) or momentum < 0:
            raise TypeError("Parameter 'momentum' must be a non-negative float")
        if not isinstance(nesterov, bool):
            raise TypeError("Parameter 'nesterov' must be boolean")
        if not isinstance(anneal, numbers.Real) or anneal <= 0:
            raise TypeError("Parameter 'anneal' must be a positive float")
        if not isinstance(iterations, numbers.Integral) or iterations <= 0:
            raise TypeError("Parameter 'iterations' must be a positive int")

        self.rate = rate
        self.momentum = momentum
        self.nesterov = nesterov
        self.anneal = anneal
        self.iterations = iterations

    def optimize(self, x0, func, grad=None, args=None, kwargs=None,
                 callback=None):
        """Approximate a minimizer of the objective function.

        Parameters
        ----------
        func: callable
            The objective function to minimize.
        x0: array-like
            Initial guess for the minimizer.
        grad: callable, optional
            Gradient/Jacobian (vector of first derivatives) of the objective
            function. This must be a function returning a 1D array. If it is not
            specified, then `func` needs to have a 'grad' attribute.
        args: sequence, optional
            Extra positional arguments to pass to the objective function and
            gradient.
        kwargs: dict, optional
            Extra keyword arguments to pass to the objective function and
            gradient.
        callback: callable, optional
            Function to call at every iteration of the algorithm. The function
            is called on the current value of the parameter being minimized
            along with the extra arguments specified by `args` and `kwargs`.
            For example, `callback` could be a function that prints the value of
            the objective function at each iteration.

        Returns
        -------
        x : array-like
            The approximate minimizer of the objective function.
        """
        if not callable(func):
            raise ValueError(f"Objective function {func} is not callable")

        if grad is None:
            if hasattr(func, "grad"):
                grad = func.grad
            else:
                raise ValueError("Could not detect objective function gradient")
        if not callable(grad):
            raise ValueError(f"Gradient {grad} is not callable")

        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        x = np.asarray(x0)
        u = np.zeros(x.shape)
        if callback is not None:
            callback(x, *args, **kwargs)

        if self.nesterov:
            for t in range(int(self.iterations)):
                rate = self.rate / (1 + t / self.anneal)
                u_prev = u
                u = self.momentum * u - rate * grad(x, *args, **kwargs)
                x = x - self.momentum * u_prev + (1 + self.momentum) * u
                if callback is not None:
                    callback(x, *args, **kwargs)
        else:
            for t in range(int(self.iterations)):
                rate = self.rate / (1 + t / self.anneal)
                u = self.momentum * u - rate * grad(x, *args, **kwargs)
                x = x + u
                if callback is not None:
                    callback(x, *args, **kwargs)
        return x
