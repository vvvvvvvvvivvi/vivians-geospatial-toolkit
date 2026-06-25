
# ---- Publishing map logic ----
publishing_map_abbrv = ""
publishing_map_prefix = ""
publishing_map_heading = ""
publishing_map_name = ""
final_abbrv = ""

if "publishing_map" in requirements:
    
    defaults = load_defaults()

    if defaults:
        print("\nPrevious publishing values found:")
        print(f"  Abbreviation : {defaults.get('abbrv')}")
        print(f"  Map prefix   : {defaults.get('prefix')}")
        print(f"  Map heading  : {defaults.get('heading')}")

        use_defaults = input("\nUse these values? (yes/no): ").strip().lower() == "yes"
    else:
        use_defaults = False

    if use_defaults:
        publishing_map_abbrv = defaults.get("abbrv", "")
        publishing_map_prefix = defaults.get("prefix", "")
        publishing_map_heading = defaults.get("heading", "")
    else:
        publishing_map_abbrv = input("Enter project abbreviation (optional): ").strip()
        publishing_map_prefix = input("Enter map prefix: ").strip()
        publishing_map_heading = input("Enter map heading: ").strip()

        save_defaults({
            "abbrv": publishing_map_abbrv,
            "prefix": publishing_map_prefix,
            "heading": publishing_map_heading
        })

    publishing_map_name = publishing_map_abbrv + "_" + publishing_map_prefix + "_" + publishing_map_heading
    print(f"✅ Publishing map name: {publishing_map_name}")
