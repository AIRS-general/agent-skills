# Project structure for Pybind11 + C++

Three goals:
1. Clean separation of ML logic vs bindings
2. Easy extensibility (new models, datasets, utils)
3. Smooth packaging for Python (like a mini scikit-learn)

```
project/
├── CMakeLists.txt
├── pyproject.toml              # for Python packaging (PEP 517)
├── README.md
├── LICENSE

├── cpp/
│   ├── CMakeLists.txt
│   │
│   ├── core/                  # core ML abstractions
│   │   ├── model.hpp
│   │   ├── dataset.hpp
│   │   ├── tensor.hpp
│   │   └── utils.hpp
│   │
│   ├── models/                # algorithms
│   │   ├── linear_regression/
│   │   │   ├── linear_regression.hpp
│   │   │   └── linear_regression.cpp
│   │   │
│   │   ├── cubist/
│   │   │   ├── cubist.hpp
│   │   │   ├── cubist.cpp
│   │   │   └── tree.cpp
│   │   │
│   │   └── svr/
│   │       ├── svr.hpp
│   │       └── svr.cpp
│   │
│   ├── optim/                 # optimization algorithms
│   │   ├── gradient_descent.hpp
│   │   └── adam.hpp
│   │
│   ├── metrics/
│   │   ├── regression.hpp
│   │   └── classification.hpp
│   │
│   ├── bindings/              # 🔥 pybind11 layer ONLY
│   │   ├── module.cpp         # main PYBIND11_MODULE
│   │   ├── bind_models.cpp
│   │   ├── bind_core.cpp
│   │   └── bind_metrics.cpp
│   │
│   └── third_party/           # optional vendored deps
│
├── python/
│   └── mlcpp/                 # Python package
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── linear.py      # thin wrappers
│       │
│       ├── utils/
│       │   └── preprocessing.py
│       │
│       └── _core.pyi          # type hints for bindings
│
├── tests/
│   ├── cpp/
│   │   └── test_linear.cpp
│   └── python/
│       └── test_linear.py
│
└── examples/
    ├── python/
    │   └── train_linear.py
    └── cpp/
        └── train_linear.cpp
```
