#Apache Spark一键部署脚本

###前提
- 有一套Linux集群
- 主节点安装了python 2.7.5+并且安装了paramiko模块；<br/>
- 每个节点可以互相依靠主机名ping通；
- 每个节点安装了java、scala；并且每个节点的java_home一致；
- 每个节点有相同用户user；

###使用方法
####1、先编辑configures文件
以一个实例介绍，很简单的。。。
> 目前我有三个节点：master,slave1,slave2,我希望选取master作为主节点，master和slave1和slave2三个节点都运行worker；
> 那么在configures写入：
>
>  master:192.168.148.147:123456:*#带星号表示是主节点
slave1:192.168.148.148:123456#格式都是[hostname]:[ip]:[passwd], 如果是主节点+":\*"
<br/>slave2:192.168.148.149:123456
<br/>#一个空行
<br/>
spark-bin-path:~/Desktop/spark-1.4.0-bin-2.6.0.tgz<br/>
java-home:/usr/lib/jvm/jdk1.7.0_79<br/>
set-ssh-passwd:True #表示需要由本脚本来设置ssh无密码登陆

####2、进行一键盘部署
`$./oneStepDeploySpark.py username；`,完成一键部署，期间有一些交互需要输入空格、密码；
####3、测试
在主节点SPARK_HOME下运行`sbin/start-all.sh`查看是否部署成功；