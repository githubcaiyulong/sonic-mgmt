import pytest
from tests.common.helpers.assertions import pytest_assert
from tests.common.plugins.tacacs import setup_tacacs_server
from .test_ro_user import ssh_remote_run

pytestmark = [
    pytest.mark.disable_loganalyzer,
    pytest.mark.topology('any'),
    pytest.mark.device_type('vs')
]

logger = logging.getLogger(__name__)

def test_jit_user(localhost, duthosts, ptfhost, rand_one_dut_hostname, creds, test_tacacs):
    """check jit user. netuser -> netadmin -> netuser"""

    duthost = duthosts[rand_one_dut_hostname]
    dutip = duthost.host.options['inventory_manager'].get_host(duthost.hostname).vars['ansible_host']

    res = ssh_remote_run(localhost, dutip, creds['tacacs_jit_user'], creds['tacacs_jit_user_passwd'], 'cat /etc/passwd')
    for l in res['stdout_lines']:
        fds = l.split(':')
        if fds[0] == "test":
            assert fds[4] == "remote_user"

    # change jit user to netadmin
    creds['tacacs_jit_user_membership'] = 'netadmin'
    setup_tacacs_server(ptfhost, creds)

    res = ssh_remote_run(localhost, dutip, creds['tacacs_jit_user'], creds['tacacs_jit_user_passwd'], 'cat /etc/passwd')
    for l in res['stdout_lines']:
        fds = l.split(':')
        if fds[0] == "testadmin":
            assert fds[4] == "remote_user_su"

    # change jit user back to netuser
    creds['tacacs_jit_user_membership'] = 'netuser'
    setup_tacacs_server(ptfhost, creds)

    res = ssh_remote_run(localhost, dutip, creds['tacacs_jit_user'], creds['tacacs_jit_user_passwd'], 'cat /etc/passwd')
    for l in res['stdout_lines']:
        fds = l.split(':')
        if fds[0] == "test":
            assert fds[4] == "remote_user"
