# Python Basics for Scientific Computing

A quick-reference for the Python patterns used most often in the group.

## NumPy essentials

```python
import numpy as np

# Create arrays
a = np.array([1.0, 2.0, 3.0])
b = np.zeros((3, 3))
c = np.linspace(0, 10, 100)   # 100 evenly spaced points

# Array operations (element-wise)
a * 2
np.sqrt(a)
np.dot(a, a)          # dot product
np.linalg.norm(a)     # vector norm

# Slicing
data = np.loadtxt("file.dat")
x = data[:, 0]        # first column
y = data[:, 1]        # second column
y[y > 0]              # boolean mask

# Save / load
np.savetxt("out.dat", np.column_stack([x, y]))
np.save("array.npy", a)
a = np.load("array.npy")
```

## Matplotlib quick plots

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(x, y, label="my data")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
plt.tight_layout()
plt.savefig("plot.pdf")
plt.show()
```

## File I/O

```python
# Read a plain text file line by line
with open("file.txt") as f:
    for line in f:
        print(line.strip())

# Write to a file
with open("out.txt", "w") as f:
    f.write(f"value = {42}\n")

# JSON
import json
with open("params.json") as f:
    params = json.load(f)
```

## Useful one-liners

```python
# List comprehension
squares = [x**2 for x in range(10)]

# Enumerate with index
for i, val in enumerate(squares):
    print(i, val)

# Zip two lists
for x, y in zip(list_a, list_b):
    print(x, y)

# f-strings
name = "LAMMPS"
print(f"Running {name} with {96} cores")
```

## Virtual environments

```bash
# Create
python -m venv myenv

# Activate (Linux/macOS)
source myenv/bin/activate

# Activate (Windows)
myenv\Scripts\activate

# Install packages
pip install numpy matplotlib ase

# Deactivate
deactivate
```
