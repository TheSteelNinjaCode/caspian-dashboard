def layout(context_data):
    request = context_data.get("request") if context_data else None
    current_path = request.url.path if request else "/dashboard"

    if current_path == "/dashboard":
        current_section = "Overview"
    else:
        current_section = current_path.rstrip("/").split("/")[-1].replace("-", " ").title()

    return {
        "current_section": current_section,
        "is_overview": current_path == "/dashboard",
        "is_users": current_path.startswith("/dashboard/users"),
    }
