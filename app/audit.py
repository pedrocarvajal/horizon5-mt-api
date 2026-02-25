import structlog

logger = structlog.get_logger("audit")


def log_login_success(user_id, ip):
    logger.info("login_success", user_id=str(user_id), ip=ip)


def log_login_failed(email, ip, reason):
    logger.warning("login_failed", email=email, ip=ip, reason=reason)


def log_account_locked(email, ip, failed_attempts):
    logger.warning("account_locked", email=email, ip=ip, failed_attempts=failed_attempts)


def log_token_blacklisted(user_id):
    logger.info("token_blacklisted", user_id=str(user_id))


def log_role_changed(user_id, old_role, new_role, changed_by):
    logger.warning(
        "role_changed",
        user_id=str(user_id),
        old_role=old_role,
        new_role=new_role,
        changed_by=str(changed_by),
    )


def log_account_created(account_id, created_by):
    logger.info("account_created", account_id=str(account_id), created_by=str(created_by))


def log_account_deleted(account_id, deleted_by):
    logger.warning("account_deleted", account_id=str(account_id), deleted_by=str(deleted_by))


def log_permission_denied(user_id, ip, path, method):
    logger.warning("permission_denied", user_id=str(user_id), ip=ip, path=path, method=method)
