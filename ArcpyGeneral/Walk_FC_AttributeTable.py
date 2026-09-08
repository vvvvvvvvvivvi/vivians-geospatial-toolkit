import arcpy
fc_path = r"\path\to.gdbeaturename"

fields = arcpy.ListFields(fc_path)

print(f"\nDataset: {fc_path}")
print("=" * 120)

for field in fields:
    print(
        f"Name={field.name} | "
        f"Alias={field.aliasName} | "
        f"Type={field.type} | "
        f"Length={field.length} | "
        f"Nullable={field.isNullable} | "
        f"Required={field.required}"
    )

print("=" * 120)
print(f"Field count: {len(fields)}")
