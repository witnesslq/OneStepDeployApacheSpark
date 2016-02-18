#!/usr/bin/env python

import os
import sys
import paramiko

paramiko.util.log_to_file('spark-ssh.log')

class Computer:
    def __init__(self, hostname, ip, user, passwd):
        self.__host, self.__ip, self.__user, self.__passwd = hostname, ip, user, passwd
    def __str__(self):
        return '%s@%s(%s)' % (self.__user, self.__host, self.__ip)
    @property
    def host(self): return self.__host
    @property
    def ip(self): return self.__ip
    @property
    def user(self): return self.__user
    @property
    def passwd(self): return self.__passwd

def printInformation(status, information):
    colorStyles = {'INFO': ('0', '37'), 'ERROR': ('1', '31'), 'SUCCESS': ('0', '32')}
    print '\033[%s;%sm[%s]%s\033[0m' % (colorStyles[status][0], colorStyles[status][1], status, information)

def getHosts2Ip(user):
    printInformation('INFO', 'now reading the configure file...')
    master = None
    slaves = []
    settings = {}
    with open('configures', 'r') as inputfile:
        for line in inputfile:
            lineAttrs = line.strip().split(':')
            if len(lineAttrs) < 3: break
            hostname, ip, passwd = lineAttrs[0], lineAttrs[1], lineAttrs[2]
            if len(lineAttrs) == 4:
                master = Computer(hostname, ip, user, passwd)
            else:
                slaves.append(Computer(hostname, ip, user, passwd))
        for line in inputfile:
            lineAttrs = line.strip().split(':')
            settings[lineAttrs[0]] = lineAttrs[1]
    printInformation('INFO', 'master is %s' % master)
    for slave in slaves: printInformation('INFO', 'slave is %s' % slave)
    for conf_key in settings: printInformation('INFO', '%s = %s' % (conf_key, settings[conf_key]))
    return master, slaves, settings

def remoteSshNoPasswd(host, user, passwd):
    if os.system('scp ~/.ssh/id_rsa.pub %s@%s:~/id_rsa_from_master' % (user, host)):
        printInformation('ERROR', 'when scp id_rsa.pub to %s' % host)
        return False
    else:
        printInformation('SUCCESS', 'scp id_rsa.pub to %s' % host)
    try:
        printInformation('INFO', 'now ssh connect to %s@%s...' % (user, host))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, 22, user, passwd, timeout=5)
        ssh.exec_command('cat ~/id_rsa_from_master >> ~/.ssh/authorized_keys')
        ssh.exec_command('chmod 600 ~/.ssh/authorized_keys')
    except:
        printInformation('ERROR', 'when ssh to %s' % host)
        return False
    return True

def setNoPasswd(slaves):
    printInformation('INFO', 'now set ssh no passwd...')
    os.system('ssh-keygen -t rsa -P \'\'')
    os.system('cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys')
    os.system('chmod 600 ~/.ssh/authorized_keys')
    for slave in slaves:
        if not remoteSshNoPasswd(slave.host, slave.user, slave.passwd): return False
    printInformation('SUCCESS', 'set ssh no passwd')
    return True

def deploySpark2Remote(master, slaves, settings, user):
    spark_bin_path = settings['spark-bin-path']
    spark_bin_name = spark_bin_path.split('/')[-1][:-4]
    home_dir_path = '/home/%s' % user
    spark_dir_path = home_dir_path + '/' + spark_bin_name
    #copy and unzip finished!
    printInformation('INFO', 'now unzip spark bin package local.')
    os.system('tar zxvf %s -C %s/' % (spark_bin_path, home_dir_path))
    #configure spark-env.sh
    printInformation('INFO', 'now write conf/spark-env.sh and conf/slaves in local')
    with open(spark_dir_path + '/conf/spark-env.sh', 'w') as cf:
        cf.write('#!/usr/bin/env bash\n')
        cf.write('export JAVA_HOME=%s\n' % settings['java-home'])
        cf.write('export SPARK_HOME=%s\n' % spark_dir_path)
        cf.write('SPARK_MASTER_IP=%s\n' % master.host)
        cf.write('SPARK_MASTER_PORT=7077\n')
        cf.write('SPARK_WORKER_CORES=1\n')

    os.system('chmod +x %s/conf/spark-env.sh' % spark_dir_path)
    #configure slaves
    with open(spark_dir_path + '/conf/slaves', 'w') as cf:
        cf.write('%s\n' % master.host)
        for slave in slaves: cf.write('%s\n' % slave.host)
    #scp to here...
    printInformation('INFO', 'now scp spark project to slaves...')
    for slave in slaves:
        if os.system('scp -r %s %s@%s:%s/' % (spark_dir_path, slave.user, slave.host, home_dir_path)):
            printInformation('ERROR', 'when scp spark project to %s' % slave.host)
        else:
            printInformation('INFO', 'scp spark project to %s' % slave.host)
    printInformation('SUCCESS', 'deploy Apache Spark!')
    return True

def main():
    user = sys.argv[1]
    master, slaves, settings = getHosts2Ip(user)
    needsetssh = False
    if 'set-ssh-passwd' in settings and settings['set-ssh-passwd'] == 'True': needsetssh = True
    if needsetssh and not setNoPasswd(slaves): return
    if not deploySpark2Remote(master, slaves, settings, user): return
    printInformation('INFO', 'all done.')

if __name__ == '__main__':
    print 'USAGE:python oneStepDeploySpark.py node-user-name'
    main()