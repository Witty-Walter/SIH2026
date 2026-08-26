import copernicusmarine

result = copernicusmarine.describe(contains=["bgc", "anfc"])
for product in result.products:
    for ds in product.datasets:
        if "bgc" in ds.dataset_id and "anfc" in ds.dataset_id:
            print(f"dataset_id: {ds.dataset_id}")
            try:
                vars = [v.short_name for v in ds.versions[0].parts[0].services[0].variables]
                chl_vars = [v for v in vars if "chl" in v.lower()]
                if chl_vars:
                    print(f"  --> CHL vars: {chl_vars}")
            except Exception:
                pass
            print()
