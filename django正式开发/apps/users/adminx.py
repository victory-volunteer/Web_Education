import xadmin

from apps.users.models import EmailVerifyRecord


class EmailVerifyRecordAdmin(object):
    pass


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
