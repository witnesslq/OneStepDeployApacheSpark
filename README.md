#Apache Spark standalone一键部署脚本
###适用于
- 快速部署standalone模式进行实验
- 快速部署来运行spark程序

###前提
- 有一套Linux集群
- 主节点安装了python 2.7.5+并且安装了**paramiko**模块；
- 每个节点可以互相依靠主机名ping通
- 每个节点安装了java、scala；并且每个节点的java_home一致
- 每个节点有相同用户user

###使用方法
####1、先编辑configures文件
以一个实例介绍，很简单的。。。
> 目前我有三个节点：master,slave1,slave2,我希望选取master作为主节点，master和slave1和slave2三个节点都运行worker；
> 那么在configures写入：
>
>  ```
> master:192.168.148.147:123456:*#带星号表示是主节点
slave1:192.168.148.148:123456#格式都是[hostname]:[ip]:[passwd], 如果是主节点+":\*"
slave2:192.168.148.149:123456
#一个空行隔开
spark-bin-path:~/Desktop/spark-1.4.0-bin-2.6.0.tgz#设置spark的项目包在本地的位置
java-home:/usr/lib/jvm/jdk1.7.0_79#设置每个节点的JAVA_HOME
set-ssh-passwd:True #表示需要由本脚本来设置ssh无密码登陆，否则不需要这行```

####2、进行一键盘部署
`$./oneStepDeploySpark.py user`<br/>
输入节点们的用户名，完成一键部署<br/>
> Note：如果没有事先设置ssh无密码登陆的话，期间有一些交互需要输入空格、ssh登陆的user密码。

####3、测试
在主节点SPARK_HOME下运行`sbin/start-all.sh`查看是否部署成功。

####4、联系

初次开发，如果有问题联系leechan8@outlook.com，必迅速回复