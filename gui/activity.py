def log(db, user, action, module, description):
    """Record an audit log entry using the given user (dict may be None/empty)."""
    user = user or {}
    db.log_activity(
        user_id=user.get("id"),
        username=user.get("username"),
        role=user.get("role"),
        action=action,
        module=module,
        description=description,
    )
