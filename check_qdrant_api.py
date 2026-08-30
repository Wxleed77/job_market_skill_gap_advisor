from qdrant_client import QdrantClient

c = QdrantClient(':memory:')
methods = sorted([m for m in dir(c) if not m.startswith('_')])
print(f"Total methods: {len(methods)}\n")

print("All public methods:")
for m in methods:
    print(f"  {m}")

